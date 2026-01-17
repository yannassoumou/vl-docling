"""
Query Result Saver

Saves query results (raw retrieval and reranked) to disk for evaluation and reuse.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class QueryResultSaver:
    """Saves query results to disk for evaluation and reuse."""
    
    def __init__(self, output_dir: str = "query_results"):
        """
        Initialize the query result saver.
        
        Args:
            output_dir: Directory to save query results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for use in filename.
        
        Args:
            text: Text to sanitize
            max_length: Maximum length of sanitized text
            
        Returns:
            Sanitized text safe for filenames
        """
        # Remove special characters
        sanitized = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' for c in text)
        # Replace spaces with underscores
        sanitized = sanitized.replace(' ', '_')
        # Truncate to max length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        # Remove trailing underscores
        sanitized = sanitized.rstrip('_')
        return sanitized
    
    def save_query_results(
        self,
        query: str,
        raw_results: List[Dict[str, Any]],
        reranked_results: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Save query results to disk.
        
        Args:
            query: The search query
            raw_results: Raw retrieval results from vector search
            reranked_results: Reranked results (if reranker is enabled)
            metadata: Additional metadata to save
            
        Returns:
            Path to the saved results directory
        """
        # Create timestamp and sanitized query for folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_slug = self._sanitize_filename(query)
        folder_name = f"{timestamp}_{query_slug}"
        
        # Create folder for this query
        query_dir = os.path.join(self.output_dir, folder_name)
        os.makedirs(query_dir, exist_ok=True)
        
        # Prepare metadata
        full_metadata = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "raw_result_count": len(raw_results),
            "reranked_result_count": len(reranked_results) if reranked_results else 0,
            "reranker_used": reranked_results is not None,
        }
        
        if metadata:
            full_metadata.update(metadata)
        
        # Save query metadata
        metadata_path = os.path.join(query_dir, "query_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(full_metadata, f, indent=2, ensure_ascii=False)
        
        # Save raw retrieval results
        raw_path = os.path.join(query_dir, "raw_retrieval.json")
        raw_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": len(raw_results),
            "results": self._prepare_results_for_json(raw_results)
        }
        with open(raw_path, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        
        # Save reranked results (if available)
        if reranked_results:
            reranked_path = os.path.join(query_dir, "reranked_results.json")
            reranked_data = {
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "result_count": len(reranked_results),
                "results": self._prepare_results_for_json(reranked_results)
            }
            with open(reranked_path, 'w', encoding='utf-8') as f:
                json.dump(reranked_data, f, indent=2, ensure_ascii=False)
        
        print(f"[INFO] Query results saved to: {query_dir}")
        return query_dir
    
    def _prepare_results_for_json(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Prepare results for JSON serialization.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            JSON-serializable list of results
        """
        json_results = []
        
        for result in results:
            json_result = {
                "content": result.get('content', ''),
                "score": float(result.get('score', 0.0)),
                "chunk_id": result.get('chunk_id'),
                "metadata": result.get('metadata', {}),
            }
            
            # Add reranking information if available
            if 'rerank_score' in result:
                json_result['rerank_score'] = float(result['rerank_score']) if result['rerank_score'] is not None else None
            
            if 'original_rank' in result:
                json_result['original_rank'] = result['original_rank']
            
            if 'new_rank' in result:
                json_result['new_rank'] = result['new_rank']
            
            json_results.append(json_result)
        
        return json_results
    
    def load_query_results(self, query_dir: str) -> Dict[str, Any]:
        """
        Load saved query results from disk.
        
        Args:
            query_dir: Path to the query results directory
            
        Returns:
            Dictionary with query, metadata, raw_results, and reranked_results
        """
        result = {}
        
        # Load metadata
        metadata_path = os.path.join(query_dir, "query_metadata.json")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r', encoding='utf-8') as f:
                result['metadata'] = json.load(f)
        
        # Load raw results
        raw_path = os.path.join(query_dir, "raw_retrieval.json")
        if os.path.exists(raw_path):
            with open(raw_path, 'r', encoding='utf-8') as f:
                result['raw'] = json.load(f)
        
        # Load reranked results
        reranked_path = os.path.join(query_dir, "reranked_results.json")
        if os.path.exists(reranked_path):
            with open(reranked_path, 'r', encoding='utf-8') as f:
                result['reranked'] = json.load(f)
        
        return result
    
    def list_saved_queries(self) -> List[Dict[str, Any]]:
        """
        List all saved query results.
        
        Returns:
            List of dictionaries with query information
        """
        queries = []
        
        if not os.path.exists(self.output_dir):
            return queries
        
        for folder_name in sorted(os.listdir(self.output_dir), reverse=True):
            folder_path = os.path.join(self.output_dir, folder_name)
            
            if not os.path.isdir(folder_path):
                continue
            
            metadata_path = os.path.join(folder_path, "query_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    metadata['folder'] = folder_name
                    metadata['path'] = folder_path
                    queries.append(metadata)
        
        return queries


if __name__ == "__main__":
    # Example usage
    saver = QueryResultSaver()
    
    # Example query results
    query = "What is machine learning?"
    
    raw_results = [
        {
            "content": "Machine learning is a subset of artificial intelligence...",
            "score": 0.95,
            "chunk_id": 1,
            "metadata": {"source": "ml_intro.pdf", "page": 1}
        },
        {
            "content": "Deep learning is a type of machine learning...",
            "score": 0.87,
            "chunk_id": 2,
            "metadata": {"source": "dl_basics.pdf", "page": 1}
        }
    ]
    
    reranked_results = [
        {
            "content": "Machine learning is a subset of artificial intelligence...",
            "score": 0.95,
            "rerank_score": 0.98,
            "original_rank": 1,
            "new_rank": 1,
            "chunk_id": 1,
            "metadata": {"source": "ml_intro.pdf", "page": 1}
        },
        {
            "content": "Deep learning is a type of machine learning...",
            "score": 0.87,
            "rerank_score": 0.85,
            "original_rank": 2,
            "new_rank": 2,
            "chunk_id": 2,
            "metadata": {"source": "dl_basics.pdf", "page": 1}
        }
    ]
    
    # Save results
    result_dir = saver.save_query_results(query, raw_results, reranked_results)
    print(f"\nResults saved to: {result_dir}")
    
    # Load results back
    loaded = saver.load_query_results(result_dir)
    print(f"\nLoaded query: {loaded['metadata']['query']}")
    print(f"Raw results: {loaded['raw']['result_count']}")
    print(f"Reranked results: {loaded['reranked']['result_count']}")
    
    # List all saved queries
    print("\nAll saved queries:")
    for q in saver.list_saved_queries():
        print(f"  - {q['timestamp']}: {q['query'][:50]}...")
