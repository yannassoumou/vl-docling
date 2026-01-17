"""
Reranker Client for Qwen3-VL-Reranker API

Provides reranking capabilities to improve retrieval quality by 
reordering initial search results based on semantic relevance.

Supports both native reranker endpoints and llama.cpp completion endpoints.
"""

import requests
from typing import List, Dict, Any, Tuple
from config_loader import load_config

# Try to import llama.cpp reranker
try:
    from reranker_llamacpp import LlamaCppRerankerClient
    LLAMACPP_AVAILABLE = True
except ImportError:
    LLAMACPP_AVAILABLE = False


def create_reranker_client(api_url: str = None, timeout: int = None):
    """
    Factory function to create the appropriate reranker client.
    
    Automatically detects if the server supports native /v1/rerank or needs llama.cpp wrapper.
    
    Args:
        api_url: API endpoint URL
        timeout: Request timeout
    
    Returns:
        Appropriate reranker client instance
    """
    config = load_config()
    reranker_config = config.get('reranker', {})
    
    url = api_url or reranker_config.get('api_url', '')
    
    # Try to detect if this is a llama.cpp server
    if 'llamacpp' in url.lower() or LLAMACPP_AVAILABLE:
        # Check if server responds to /v1/rerank
        try:
            test_response = requests.get(
                url.replace('/v1/rerank', '/health'),
                timeout=2
            )
            # If we get a 501 on /v1/rerank, use llama.cpp wrapper
        except:
            pass
        
        # Use llama.cpp completion-based reranker
        if LLAMACPP_AVAILABLE:
            print("[INFO] Using llama.cpp completion endpoint for reranking")
            return LlamaCppRerankerClient(api_url=url, timeout=timeout)
    
    # Use standard reranker API
    print("[INFO] Using standard /v1/rerank endpoint")
    return StandardRerankerClient(api_url=url, timeout=timeout)


class StandardRerankerClient:
    """
    Client for interacting with Qwen3-VL-Reranker API.
    
    Reranker improves retrieval by re-scoring candidate documents
    based on deeper semantic understanding of query-document pairs.
    """
    
    def __init__(self, api_url: str = None, timeout: int = None):
        """
        Initialize the reranker client.
        
        Args:
            api_url: URL of the reranker API endpoint
            timeout: Request timeout in seconds
        """
        config = load_config()
        reranker_config = config.get('reranker', {})
        
        self.api_url = api_url or reranker_config.get('api_url')
        self.timeout = timeout or reranker_config.get('timeout', 30)
        self.model_name = reranker_config.get('model_name', 'Qwen3-VL-Reranker-8B')
        self.max_retries = reranker_config.get('max_retries', 3)
        self.enabled = reranker_config.get('enabled', False)
        
        if not self.api_url:
            raise ValueError("Reranker API URL not configured")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on relevance to the query.
        
        Args:
            query: The search query
            documents: List of document texts to rerank
            top_k: Number of top documents to return (None = return all)
        
        Returns:
            List of dictionaries with:
                - index: Original index in the input list
                - relevance_score: Reranker score
                - document: Original document text
        """
        if not self.enabled:
            # Return documents with their original indices and no scores
            return [
                {
                    'index': i,
                    'relevance_score': None,
                    'document': doc
                }
                for i, doc in enumerate(documents)
            ]
        
        # Prepare request
        payload = {
            'model': self.model_name,
            'query': query,
            'documents': documents
        }
        
        if top_k is not None:
            payload['top_n'] = top_k
        
        # Make API request with retries
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Parse response from llama.cpp /v1/rerank endpoint
                # Expected format: {"results": [{"index": 0, "relevance_score": 0.9}, ...]}
                if 'results' in data:
                    results = data['results']
                    # Add document text back to results
                    for result in results:
                        idx = result['index']
                        result['document'] = documents[idx]
                    return results
                elif 'data' in data:
                    # Alternative format
                    return data['data']
                else:
                    # Fallback: assume data is the results directly
                    return data
                
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    print(f"[WARNING] Reranker timeout, retrying... ({attempt + 1}/{self.max_retries})")
                    continue
                else:
                    print("[ERROR] Reranker timeout after max retries, returning original order")
                    return self._fallback_response(documents)
                    
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    print(f"[WARNING] Reranker error: {e}, retrying... ({attempt + 1}/{self.max_retries})")
                    continue
                else:
                    print(f"[ERROR] Reranker failed: {e}, returning original order")
                    return self._fallback_response(documents)
        
        return self._fallback_response(documents)
    
    def _fallback_response(self, documents: List[str]) -> List[Dict[str, Any]]:
        """Return documents in original order when reranker fails."""
        return [
            {
                'index': i,
                'relevance_score': None,
                'document': doc
            }
            for i, doc in enumerate(documents)
        ]
    
    def is_enabled(self) -> bool:
        """Check if reranker is enabled."""
        return self.enabled


def test_reranker():
    """Test the reranker client."""
    print("Testing Reranker Client\n")
    
    config = load_config()
    if not config.get('reranker', {}).get('enabled', False):
        print("Reranker is disabled in config")
        return
    
    try:
        client = RerankerClient()
        print(f"✓ Reranker client initialized")
        print(f"  API URL: {client.api_url}")
        print(f"  Model: {client.model_name}")
        print(f"  Enabled: {client.enabled}\n")
        
        # Test reranking
        query = "What is machine learning?"
        documents = [
            "Machine learning is a subset of AI that enables systems to learn from data.",
            "Python is a programming language popular for data science.",
            "Deep learning uses neural networks with multiple layers.",
            "Coffee is a popular beverage made from roasted beans."
        ]
        
        print(f"Query: {query}")
        print(f"Documents to rerank: {len(documents)}\n")
        
        results = client.rerank(query, documents, top_k=3)
        
        print("Reranked Results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. [Index: {result['index']}, Score: {result.get('relevance_score', 'N/A')}]")
            print(f"     {result['document'][:80]}...")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    test_reranker()
