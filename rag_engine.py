import os
from typing import List, Dict, Any, Optional, Union

from embedding_client import QwenEmbeddingClient
from document_processor import Document, DocumentProcessor
from vector_store import VectorStore
from milvus_store import MilvusStore
from vector_store_factory import create_vector_store
from config import TOP_K
from config_loader import load_config

# Try to import reranker
try:
    from reranker_client import StandardRerankerClient
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine.
    
    This engine handles document ingestion, vector storage, and retrieval.
    Note: This implementation focuses on retrieval. For generation, you would
    need to integrate with a language model API.
    """
    
    def __init__(
        self,
        embedding_client: QwenEmbeddingClient = None,
        vector_store: Union[VectorStore, MilvusStore] = None,
        document_processor: DocumentProcessor = None,
        top_k: int = TOP_K,
        store_type: str = None,
        **store_kwargs
    ):
        """
        Initialize the RAG engine.
        
        Args:
            embedding_client: Client for generating embeddings
            vector_store: Vector store for document chunks (if None, created from store_type)
            document_processor: Processor for documents
            top_k: Number of documents to retrieve
            store_type: Type of vector store ('faiss' or 'milvus'). Used if vector_store is None.
            **store_kwargs: Additional arguments for vector store creation
        """
        self.embedding_client = embedding_client or QwenEmbeddingClient()
        
        # Create vector store using factory if not provided
        if vector_store is None:
            self.vector_store = create_vector_store(
                store_type=store_type,
                embedding_client=self.embedding_client,
                **store_kwargs
            )
        else:
            self.vector_store = vector_store
        
        self.document_processor = document_processor or DocumentProcessor()
        self.top_k = top_k
        
        # Initialize reranker if available and enabled
        config = load_config()
        reranker_config = config.get('reranker', {})
        self.reranker_enabled = reranker_config.get('enabled', False) and RERANKER_AVAILABLE
        self.reranker = None
        
        if self.reranker_enabled:
            try:
                self.reranker = StandardRerankerClient()
                self.rerank_top_k = reranker_config.get('rerank_top_k', 20)
                self.final_top_k = reranker_config.get('final_top_k', 5)
                print(f"[INFO] Reranker enabled: retrieving {self.rerank_top_k} candidates, reranking to top {self.final_top_k}")
            except Exception as e:
                print(f"[WARNING] Reranker enabled but failed to initialize: {e}")
                self.reranker_enabled = False
    
    def ingest_text(self, text: str, metadata: Dict[str, Any] = None):
        """
        Ingest a text string into the RAG system.
        
        Args:
            text: The text to ingest
            metadata: Optional metadata for the text
        """
        document = Document(content=text, metadata=metadata or {})
        chunks = self.document_processor.chunk_document(document)
        self.vector_store.add_chunks(chunks)
    
    def ingest_file(self, file_path: str):
        """
        Ingest a file into the RAG system (supports text and PDFs).
        Uses Granite VLM for all PDF processing.
        
        Args:
            file_path: Path to the file
        """
        # Use DocumentProcessor for all files (including PDFs with Granite)
        document = self.document_processor.load_text_file(file_path)
        chunks = self.document_processor.chunk_document(document)
        self.vector_store.add_chunks(chunks)
    
    def ingest_directory(self, directory_path: str, extensions: List[str] = None, recursive: bool = True):
        """
        Ingest all files from a directory into the RAG system.
        
        Args:
            directory_path: Path to the directory
            extensions: List of file extensions to include
            recursive: If True, search subdirectories recursively (default: True)
        """
        documents = self.document_processor.load_directory(directory_path, extensions, recursive=recursive)
        
        if recursive:
            print(f"Found {len(documents)} documents in {directory_path} (including subdirectories)")
        else:
            print(f"Found {len(documents)} documents in {directory_path}")
        
        all_chunks = []
        for doc in documents:
            chunks = self.document_processor.chunk_document(doc)
            all_chunks.extend(chunks)
        
        self.vector_store.add_chunks(all_chunks)
    
    def retrieve(self, query: str, top_k: int = None, verbose: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve relevant document chunks for a query.
        
        Args:
            query: The search query
            top_k: Number of results to return (uses default if not specified)
            verbose: Show detailed reranking process
            
        Returns:
            List of dictionaries with chunk content, metadata, and scores
        """
        k = top_k or self.top_k
        
        # If reranker is enabled, retrieve more candidates for reranking
        if self.reranker_enabled and self.reranker:
            initial_k = max(self.rerank_top_k, k)
            results = self.vector_store.search(query, top_k=initial_k)
            
            # Convert to list for reranking
            initial_results = [
                {
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'score': score,
                    'chunk_id': chunk.chunk_id,
                    'original_rank': i + 1
                }
                for i, (chunk, score) in enumerate(results)
            ]
            
            if verbose:
                print("\n" + "="*80)
                print("RERANKER ANALYSIS")
                print("="*80)
                print(f"\n[STEP 1] Initial Retrieval: Top {len(initial_results)} candidates from vector search\n")
                for i, res in enumerate(initial_results[:10], 1):  # Show top 10
                    source = res['metadata'].get('source', 'Unknown')
                    filename = os.path.basename(source) if source != 'Unknown' else 'Unknown'
                    print(f"  {i}. Score: {res['score']:.4f} | {filename}")
            
            # Prepare documents for reranking
            documents = [res['content'] for res in initial_results]
            
            # Rerank
            try:
                if verbose:
                    print(f"\n[STEP 2] Reranking with Qwen3-VL-Reranker...\n")
                
                reranked = self.reranker.rerank(query, documents, top_k=k)
                
                # Map reranked results back to original results
                final_results = []
                for rerank_result in reranked:
                    idx = rerank_result['index']
                    original = initial_results[idx]
                    original['rerank_score'] = rerank_result.get('relevance_score')
                    original['new_rank'] = len(final_results) + 1
                    final_results.append(original)
                
                if verbose:
                    print(f"[STEP 3] After Reranking: Top {len(final_results)} results\n")
                    for res in final_results:
                        source = res['metadata'].get('source', 'Unknown')
                        filename = os.path.basename(source) if source != 'Unknown' else 'Unknown'
                        rank_change = res['original_rank'] - res['new_rank']
                        # Use ASCII characters for Windows console compatibility
                        change_indicator = f"(+{rank_change})" if rank_change > 0 else f"(-{abs(rank_change)})" if rank_change < 0 else "(=)"
                        rerank_score = res.get('rerank_score', 'N/A')
                        rerank_score_str = f"{rerank_score:.4f}" if isinstance(rerank_score, (int, float)) else str(rerank_score)
                        print(f"  #{res['new_rank']} {change_indicator} | Rerank: {rerank_score_str} | Vector: {res['score']:.4f} | {filename}")
                    print("="*80 + "\n")
                
                return final_results
                
            except Exception as e:
                if verbose:
                    print(f"\n[WARNING] Reranking failed: {e}")
                    print("[FALLBACK] Using initial vector search results\n")
                    print("="*80 + "\n")
                return initial_results[:k]
        else:
            # No reranker, use standard retrieval
            results = self.vector_store.search(query, top_k=k)
            
            return [
                {
                    'content': chunk.content,
                    'metadata': chunk.metadata,
                    'score': score,
                    'chunk_id': chunk.chunk_id
                }
                for chunk, score in results
            ]
    
    def get_context(self, query: str, top_k: int = None) -> str:
        """
        Get concatenated context from retrieved chunks.
        
        Args:
            query: The search query
            top_k: Number of results to retrieve
            
        Returns:
            Concatenated text from retrieved chunks
        """
        results = self.retrieve(query, top_k)
        
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'Unknown')
            content = result['content']
            context_parts.append(f"[Source {i}: {source}]\n{content}\n")
        
        return "\n---\n".join(context_parts)
    
    def query(self, question: str, top_k: int = None, verbose: bool = False) -> Dict[str, Any]:
        """
        Query the RAG system.
        
        Args:
            question: The question to ask
            top_k: Number of documents to retrieve
            verbose: Show detailed reranking process
            
        Returns:
            Dictionary with retrieved context and metadata
        """
        retrieved_docs = self.retrieve(question, top_k, verbose=verbose)
        context = self.get_context(question, top_k)
        
        return {
            'question': question,
            'context': context,
            'retrieved_docs': retrieved_docs,
            'num_docs': len(retrieved_docs)
        }
    
    def save(self):
        """Save the RAG system state."""
        self.vector_store.save()
    
    def load(self):
        """Load the RAG system state."""
        return self.vector_store.load()
    
    def clear(self):
        """Clear the RAG system."""
        self.vector_store.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system.
        
        Returns:
            Dictionary with statistics
        """
        return self.vector_store.get_stats()


def format_rag_response(result: Dict[str, Any]) -> str:
    """
    Format RAG query result for display.
    
    Args:
        result: Result dictionary from RAG query
        
    Returns:
        Formatted string
    """
    output = []
    output.append("=" * 80)
    output.append(f"QUESTION: {result['question']}")
    output.append("=" * 80)
    output.append(f"\nRetrieved {result['num_docs']} relevant document(s):\n")
    
    for i, doc in enumerate(result['retrieved_docs'], 1):
        output.append(f"\n--- Document {i} (Score: {doc['score']:.4f}) ---")
        output.append(f"Source: {doc['metadata'].get('source', 'Unknown')}")
        if 'chunk_index' in doc['metadata']:
            output.append(f"Chunk: {doc['metadata']['chunk_index'] + 1}/{doc['metadata'].get('total_chunks', '?')}")
        output.append(f"\nContent:\n{doc['content']}\n")
    
    output.append("=" * 80)
    output.append("\nCONTEXT FOR LLM:")
    output.append("=" * 80)
    output.append(result['context'])
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test the RAG engine
    rag = RAGEngine()
    
    # Ingest some sample texts
    rag.ingest_text(
        "Python is a high-level, interpreted programming language known for its simplicity and readability.",
        metadata={'source': 'python_intro.txt', 'topic': 'programming'}
    )
    
    rag.ingest_text(
        "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience.",
        metadata={'source': 'ml_intro.txt', 'topic': 'AI'}
    )
    
    rag.ingest_text(
        "Neural networks are computing systems inspired by biological neural networks in animal brains.",
        metadata={'source': 'nn_intro.txt', 'topic': 'AI'}
    )
    
    # Query the system
    result = rag.query("What is Python?", top_k=2)
    print(format_rag_response(result))
    
    # Get stats
    print("\n\nRAG System Statistics:")
    print(rag.get_stats())
