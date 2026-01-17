import json
import numpy as np
from typing import List, Tuple, Dict, Any
from tqdm import tqdm

from pymilvus import (
    connections,
    Collection,
    CollectionSchema,
    FieldSchema,
    DataType,
    utility
)

from embedding_client import QwenEmbeddingClient
from document_processor import DocumentChunk
from config import (
    MILVUS_HOST,
    MILVUS_PORT,
    MILVUS_USER,
    MILVUS_PASSWORD,
    MILVUS_DB_NAME,
    MILVUS_COLLECTION_NAME,
    MILVUS_INDEX_TYPE,
    MILVUS_METRIC_TYPE
)


class MilvusStore:
    """Vector store for document chunks using Milvus."""
    
    def __init__(
        self,
        embedding_client: QwenEmbeddingClient = None,
        host: str = None,
        port: str = None,
        user: str = None,
        password: str = None,
        db_name: str = None,
        collection_name: str = None
    ):
        """
        Initialize the Milvus vector store.
        
        Args:
            embedding_client: Client for generating embeddings
            host: Milvus server host
            port: Milvus server port
            user: Optional username for authentication
            password: Optional password for authentication
            db_name: Database name
            collection_name: Collection name
        """
        self.embedding_client = embedding_client or QwenEmbeddingClient()
        self.host = host or MILVUS_HOST
        self.port = port or MILVUS_PORT
        self.user = user or MILVUS_USER
        self.password = password or MILVUS_PASSWORD
        self.db_name = db_name or MILVUS_DB_NAME
        self.collection_name = collection_name or MILVUS_COLLECTION_NAME
        
        self.collection = None
        self.chunks = []
        self.dimension = None
        self.connection_alias = "default"
        
        # Connect to Milvus
        self._connect()
    
    def _connect(self):
        """Connect to Milvus server."""
        try:
            # Disconnect if already connected
            try:
                connections.disconnect(self.connection_alias)
            except:
                pass
            
            # Connect with or without authentication
            if self.user and self.password:
                connections.connect(
                    alias=self.connection_alias,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    db_name=self.db_name
                )
            else:
                connections.connect(
                    alias=self.connection_alias,
                    host=self.host,
                    port=self.port,
                    db_name=self.db_name
                )
            
            print(f"✓ Connected to Milvus at {self.host}:{self.port}")
            
        except Exception as e:
            raise RuntimeError(f"Failed to connect to Milvus: {str(e)}")
    
    def _create_collection(self, dimension: int):
        """
        Create a new Milvus collection.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        # Define collection schema
        fields = [
            FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=65535)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description=f"RAG document chunks collection"
        )
        
        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema,
            using=self.connection_alias
        )
        
        self.dimension = dimension
        print(f"✓ Created collection '{self.collection_name}' with dimension {dimension}")
    
    def _create_index(self):
        """Create index for the collection."""
        index_params = {
            "index_type": MILVUS_INDEX_TYPE,
            "metric_type": MILVUS_METRIC_TYPE,
            "params": {"nlist": 128}  # For IVF_FLAT
        }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        print(f"✓ Created index: {MILVUS_INDEX_TYPE} with metric {MILVUS_METRIC_TYPE}")
    
    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = 32):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks to add
            batch_size: Number of chunks to process at once
        """
        if not chunks:
            return
        
        print(f"Adding {len(chunks)} chunks to Milvus...")
        
        # Generate embeddings in batches
        all_embeddings = []
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Generating embeddings"):
            batch = chunks[i:i + batch_size]
            texts = [chunk.content for chunk in batch]
            
            embeddings = self.embedding_client.get_embeddings(texts)
            all_embeddings.append(embeddings)
        
        # Concatenate all embeddings
        embeddings_array = np.vstack(all_embeddings)
        
        # Create collection if it doesn't exist
        if self.collection is None:
            if not utility.has_collection(self.collection_name, using=self.connection_alias):
                self._create_collection(embeddings_array.shape[1])
            else:
                self.collection = Collection(
                    name=self.collection_name,
                    using=self.connection_alias
                )
                self.dimension = embeddings_array.shape[1]
                print(f"✓ Loaded existing collection '{self.collection_name}'")
        
        # Assign chunk IDs
        start_id = len(self.chunks)
        chunk_ids = []
        contents = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = start_id + i
            chunk_ids.append(chunk.chunk_id)
            contents.append(chunk.content)
            metadatas.append(json.dumps(chunk.metadata, ensure_ascii=False))
        
        # Insert data into Milvus
        entities = [
            chunk_ids,
            embeddings_array.tolist(),
            contents,
            metadatas
        ]
        
        self.collection.insert(entities)
        self.collection.flush()
        
        # Create index if not exists
        if not self.collection.has_index():
            self._create_index()
        
        # Load collection for search
        self.collection.load()
        
        # Store chunks locally for metadata retrieval
        self.chunks.extend(chunks)
        
        print(f"Successfully added {len(chunks)} chunks. Total chunks: {len(self.chunks)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for similar chunks to the query.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of (chunk, score) tuples sorted by relevance
        """
        if self.collection is None or len(self.chunks) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_client.get_embeddings(query)
        
        # Search parameters
        search_params = {
            "metric_type": MILVUS_METRIC_TYPE,
            "params": {"nprobe": 10}
        }
        
        # Perform search
        results = self.collection.search(
            data=query_embedding.tolist(),
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["chunk_id", "content", "metadata"]
        )
        
        # Convert results
        output = []
        for hits in results:
            for hit in hits:
                chunk_id = hit.entity.get('chunk_id')
                
                # Find the chunk by ID
                chunk = None
                for c in self.chunks:
                    if c.chunk_id == chunk_id:
                        chunk = c
                        break
                
                if chunk:
                    # Convert distance to similarity score
                    # For L2 distance, lower is better
                    distance = hit.distance
                    score = 1 / (1 + distance)
                    output.append((chunk, score))
        
        return output
    
    def save(self):
        """Save the vector store metadata."""
        # Milvus data is already persisted on the server
        # We only need to save local chunk metadata
        print(f"✓ Milvus collection '{self.collection_name}' is persisted on server")
        print(f"  Chunks stored: {len(self.chunks)}")
    
    def load(self):
        """Load the vector store from Milvus."""
        try:
            # Check if collection exists
            if utility.has_collection(self.collection_name, using=self.connection_alias):
                self.collection = Collection(
                    name=self.collection_name,
                    using=self.connection_alias
                )
                
                # Load collection
                self.collection.load()
                
                # Get collection info
                num_entities = self.collection.num_entities
                
                print(f"✓ Loaded Milvus collection '{self.collection_name}'")
                print(f"  Total entities: {num_entities}")
                
                # Note: We need to rebuild the chunks list from Milvus
                # For now, we'll note that chunks metadata needs to be fetched on demand
                return True
            else:
                print(f"Collection '{self.collection_name}' does not exist yet")
                return False
                
        except Exception as e:
            print(f"Warning: Could not load collection: {str(e)}")
            return False
    
    def clear(self):
        """Clear the vector store."""
        try:
            if utility.has_collection(self.collection_name, using=self.connection_alias):
                utility.drop_collection(self.collection_name, using=self.connection_alias)
                print(f"✓ Dropped collection '{self.collection_name}'")
            
            self.collection = None
            self.chunks = []
            self.dimension = None
            
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'num_chunks': len(self.chunks),
            'dimension': self.dimension,
            'index_size': self.collection.num_entities if self.collection else 0,
            'sources': list(set(chunk.metadata.get('source', 'unknown') for chunk in self.chunks)),
            'store_type': 'milvus',
            'host': self.host,
            'port': self.port,
            'collection': self.collection_name
        }
        
        return stats
    
    def __del__(self):
        """Cleanup on deletion."""
        try:
            connections.disconnect(self.connection_alias)
        except:
            pass


if __name__ == "__main__":
    # Test the Milvus store
    from document_processor import Document, DocumentProcessor
    
    print("Testing Milvus Vector Store\n")
    
    # Create sample documents
    docs = [
        Document("Python is a high-level programming language.", {'source': 'doc1.txt'}),
        Document("Machine learning is a subset of artificial intelligence.", {'source': 'doc2.txt'}),
        Document("Neural networks are inspired by biological neurons.", {'source': 'doc3.txt'}),
    ]
    
    # Process documents
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=10)
    chunks = processor.chunk_documents(docs)
    
    # Create Milvus store
    store = MilvusStore()
    store.add_chunks(chunks)
    
    # Search
    results = store.search("What is Python?", top_k=2)
    print("\nSearch results:")
    for chunk, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {chunk.content[:100]}")
        print()
    
    # Stats
    print("\nStore statistics:")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
