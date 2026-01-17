import os
import json
import numpy as np
import faiss
from typing import List, Tuple, Dict, Any
from tqdm import tqdm

from embedding_client import QwenEmbeddingClient
from document_processor import DocumentChunk
from config import VECTOR_STORE_PATH, INDEX_FILE, METADATA_FILE


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
    
    def add_chunks(self, chunks: List[DocumentChunk], batch_size: int = 32):
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of document chunks to add
            batch_size: Number of chunks to process at once
        """
        if not chunks:
            return
        
        print(f"Adding {len(chunks)} chunks to vector store...")
        
        # Generate embeddings in batches
        all_embeddings = []
        
        for i in tqdm(range(0, len(chunks), batch_size), desc="Generating embeddings"):
            batch = chunks[i:i + batch_size]
            texts = [chunk.content for chunk in batch]
            
            embeddings = self.embedding_client.get_embeddings(texts)
            all_embeddings.append(embeddings)
        
        # Concatenate all embeddings
        embeddings_array = np.vstack(all_embeddings)
        
        # Initialize index if not already done
        if self.index is None:
            self._initialize_index(embeddings_array.shape[1])
        
        # Assign chunk IDs
        start_id = len(self.chunks)
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = start_id + i
        
        # Add to FAISS index
        ids = np.array([chunk.chunk_id for chunk in chunks], dtype=np.int64)
        self.index.add_with_ids(embeddings_array, ids)
        
        # Store chunks
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
