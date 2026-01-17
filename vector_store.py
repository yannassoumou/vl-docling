import os
import json
import numpy as np
import faiss
from typing import List, Tuple, Dict, Any
from tqdm import tqdm

from embedding_client import QwenEmbeddingClient
from document_processor import DocumentChunk
from config import VECTOR_STORE_PATH, INDEX_FILE, METADATA_FILE
from config_loader import get_config


class VectorStore:
    """Vector store for document chunks using FAISS."""
    
    def __init__(self, embedding_client: QwenEmbeddingClient = None, store_path: str = None):
        """
        Initialize the vector store.
        
        Args:
            embedding_client: Client for generating embeddings
            store_path: Path to store the index and metadata
        """
        self.embedding_client = embedding_client or QwenEmbeddingClient()
        self.store_path = store_path or VECTOR_STORE_PATH
        self.index = None
        self.chunks = []
        self.dimension = None
        
        # Create store directory if it doesn't exist
        os.makedirs(self.store_path, exist_ok=True)
    
    def _initialize_index(self, dimension: int):
        """
        Initialize a new FAISS index.
        
        Args:
            dimension: Dimension of the embedding vectors
        """
        self.dimension = dimension
        # Use L2 distance for similarity search
        self.index = faiss.IndexFlatL2(dimension)
        # Wrap with IDMap to track chunk IDs
        self.index = faiss.IndexIDMap(self.index)
    
    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = None):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks to add
            batch_size: Number of chunks to process at once (None = use config max_batch_size)
        """
        if not chunks:
            return
        
        # Get batch size from config if not provided
        if batch_size is None:
            batch_size = get_config('embedding.max_batch_size', 128)
        
        # Get embedding model version
        embedding_model_version = self.embedding_client.get_model_version()
        
        # Check for duplicates and add metadata
        new_chunks = []
        duplicate_count = 0
        
        for chunk in chunks:
            # Add embedding model version to metadata
            chunk.metadata['embedding_model_version'] = embedding_model_version
            
            # Check for duplicate using chunk-level hash (more granular) or document-level hash
            chunk_hash = chunk.metadata.get('chunk_content_hash')
            doc_hash = chunk.metadata.get('content_hash')
            
            if chunk_hash:
                # Check if we already have a chunk with this exact content
                is_duplicate = False
                for existing_chunk in self.chunks:
                    existing_chunk_hash = existing_chunk.metadata.get('chunk_content_hash')
                    if existing_chunk_hash == chunk_hash:
                        is_duplicate = True
                        duplicate_count += 1
                        break
                
                if not is_duplicate:
                    new_chunks.append(chunk)
            elif doc_hash:
                # Fallback to document-level hash if chunk hash not available
                is_duplicate = False
                for existing_chunk in self.chunks:
                    if existing_chunk.metadata.get('content_hash') == doc_hash:
                        is_duplicate = True
                        duplicate_count += 1
                        break
                
                if not is_duplicate:
                    new_chunks.append(chunk)
            else:
                # No hash available, add anyway
                new_chunks.append(chunk)
        
        if duplicate_count > 0:
            print(f"  Skipped {duplicate_count} duplicate chunk(s) based on content hash")
        
        if not new_chunks:
            print("No new chunks to add (all were duplicates)")
            return
        
        print(f"Adding {len(new_chunks)} chunks to vector store...")
        
        # Generate embeddings in batches (using max_batch_size for optimal performance)
        all_embeddings = []
        
        # Use async if enabled, otherwise sync
        async_enabled = get_config('embedding.async_enabled', True)
        
        if async_enabled and hasattr(self.embedding_client, 'get_embeddings_async_batch'):
            # Prepare batches for async processing
            text_batches = []
            for i in range(0, len(new_chunks), batch_size):
                batch = new_chunks[i:i + batch_size]
                texts = [chunk.content for chunk in batch]
                text_batches.append(texts)
            
            # Get embeddings asynchronously
            print(f"  Using async embedding generation with {len(text_batches)} batch(es)...")
            try:
                embedding_batches = self.embedding_client.get_embeddings_async_batch(text_batches)
                # embedding_batches is a list of numpy arrays, one per batch
                all_embeddings = embedding_batches
            except Exception as e:
                print(f"  Async embedding failed: {e}, falling back to sync")
                # Fallback to synchronous processing
                for i in tqdm(range(0, len(new_chunks), batch_size), desc="Generating embeddings"):
                    batch = new_chunks[i:i + batch_size]
                    texts = [chunk.content for chunk in batch]
                    embeddings = self.embedding_client.get_embeddings(texts)
                    all_embeddings.append(embeddings)
        else:
            # Synchronous processing
            for i in tqdm(range(0, len(new_chunks), batch_size), desc="Generating embeddings"):
                batch = new_chunks[i:i + batch_size]
                texts = [chunk.content for chunk in batch]
                
                embeddings = self.embedding_client.get_embeddings(texts)
                all_embeddings.append(embeddings)
        
        # Ensure all_embeddings is a list of arrays
        if not isinstance(all_embeddings, list) or len(all_embeddings) == 0:
            raise ValueError(f"Expected non-empty list of embeddings, got: {type(all_embeddings)}")
        
        # Concatenate all embeddings
        embeddings_array = np.vstack(all_embeddings)
        
        # Initialize index if not already done
        if self.index is None:
            self._initialize_index(embeddings_array.shape[1])
        
        # Assign chunk IDs
        start_id = len(self.chunks)
        for i, chunk in enumerate(new_chunks):
            chunk.chunk_id = start_id + i
        
        # Add to FAISS index
        ids = np.array([chunk.chunk_id for chunk in new_chunks], dtype=np.int64)
        self.index.add_with_ids(embeddings_array, ids)
        
        # Store chunks
        self.chunks.extend(new_chunks)
        
        print(f"Successfully added {len(new_chunks)} chunks. Total chunks: {len(self.chunks)}")
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Search for similar chunks to the query.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of (chunk, score) tuples sorted by relevance
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.embedding_client.get_embeddings(query)
        
        # Search in FAISS index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Retrieve chunks and scores
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx >= 0 and idx < len(self.chunks):
                chunk = self.chunks[idx]
                # Convert L2 distance to similarity score (lower is better, so invert)
                score = 1 / (1 + distance)
                results.append((chunk, score))
        
        return results
    
    def save(self):
        """Save the vector store to disk."""
        if self.index is None:
            print("Warning: No index to save")
            return
        
        index_path = os.path.join(self.store_path, INDEX_FILE)
        metadata_path = os.path.join(self.store_path, METADATA_FILE)
        
        # Save FAISS index
        faiss.write_index(self.index, index_path)
        
        # Save metadata (chunks without embeddings)
        metadata = {
            'dimension': self.dimension,
            'num_chunks': len(self.chunks),
            'chunks': [
                {
                    'chunk_id': chunk.chunk_id,
                    'content': chunk.content,
                    'metadata': chunk.metadata
                }
                for chunk in self.chunks
            ]
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"Vector store saved to {self.store_path}")
    
    def load(self):
        """Load the vector store from disk."""
        index_path = os.path.join(self.store_path, INDEX_FILE)
        metadata_path = os.path.join(self.store_path, METADATA_FILE)
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print("Warning: Vector store files not found")
            return False
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load metadata
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        self.dimension = metadata['dimension']
        
        # Reconstruct chunks
        self.chunks = []
        for chunk_data in metadata['chunks']:
            chunk = DocumentChunk(
                content=chunk_data['content'],
                metadata=chunk_data['metadata'],
                chunk_id=chunk_data['chunk_id']
            )
            self.chunks.append(chunk)
        
        print(f"Vector store loaded from {self.store_path}")
        print(f"Total chunks: {len(self.chunks)}")
        return True
    
    def clear(self):
        """Clear the vector store."""
        self.index = None
        self.chunks = []
        self.dimension = None
        print("Vector store cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'num_chunks': len(self.chunks),
            'dimension': self.dimension,
            'index_size': self.index.ntotal if self.index else 0,
            'sources': list(set(chunk.metadata.get('source', 'unknown') for chunk in self.chunks))
        }


if __name__ == "__main__":
    # Test the vector store
    from document_processor import Document, DocumentProcessor
    
    # Create sample documents
    docs = [
        Document("Python is a high-level programming language.", {'source': 'doc1.txt'}),
        Document("Machine learning is a subset of artificial intelligence.", {'source': 'doc2.txt'}),
        Document("Neural networks are inspired by biological neurons.", {'source': 'doc3.txt'}),
    ]
    
    # Process documents
    processor = DocumentProcessor(chunk_size=100, chunk_overlap=10)
    chunks = processor.chunk_documents(docs)
    
    # Create vector store
    store = VectorStore()
    store.add_chunks(chunks)
    
    # Search
    results = store.search("What is Python?", top_k=2)
    print("\nSearch results:")
    for chunk, score in results:
        print(f"Score: {score:.4f}")
        print(f"Content: {chunk.content[:100]}")
        print()
