"""
Reranker Client for Qwen3-VL-Reranker via llama.cpp completion endpoint

Since llama-server doesn't support /v1/rerank, we use the completion endpoint
with proper prompting to get reranking scores.
"""

import requests
import json
from typing import List, Dict, Any
from config_loader import load_config


class LlamaCppRerankerClient:
    """
    Client for Qwen3-VL-Reranker via llama.cpp completion endpoint.
    
    Converts reranking requests to completion format that llama-server understands.
    """
    
    def __init__(self, api_url: str = None, timeout: int = None):
        """
        Initialize the reranker client.
        
        Args:
            api_url: Base URL of the llama-server (e.g., http://100.126.235.19:1111)
            timeout: Request timeout in seconds
        """
        config = load_config()
        reranker_config = config.get('reranker', {})
        
        # Get base URL (remove /v1/rerank if present)
        base_url = api_url or reranker_config.get('api_url', '')
        if '/v1/rerank' in base_url:
            base_url = base_url.replace('/v1/rerank', '')
        
        # Use completion endpoint
        self.api_url = f"{base_url}/v1/completions"
        self.timeout = timeout or reranker_config.get('timeout', 60)
        self.model_name = reranker_config.get('model_name', 'Qwen3-VL-Reranker-8B')
        self.max_retries = reranker_config.get('max_retries', 3)
        self.enabled = reranker_config.get('enabled', False)
        
        if not base_url:
            raise ValueError("Reranker API URL not configured")
    
    def _create_rerank_prompt(self, query: str, document: str, doc_idx: int) -> str:
        """
        Create a prompt for reranking using Qwen3-VL-Reranker format.
        
        The model expects a specific format to output relevance scores.
        """
        # Qwen3-VL-Reranker format: prompt the model to score relevance
        prompt = f"""Query: {query}
Document: {document}

Rate the relevance of the document to the query on a scale from 0 to 1, where:
- 0 = completely irrelevant
- 1 = perfectly relevant

Relevance score:"""
        
        return prompt
    
    def _extract_score(self, completion_text: str) -> float:
        """
        Extract relevance score from completion text.
        
        Expected formats:
        - "0.95"
        - "Relevance score: 0.85"
        - "0.7/1.0"
        """
        text = completion_text.strip()
        
        # Try to find a decimal number between 0 and 1
        import re
        
        # Look for patterns like "0.XX" or "1.0" or "0.X"
        matches = re.findall(r'\b[01]?\.\d+\b', text)
        if matches:
            score = float(matches[0])
            return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1
        
        # Look for whole numbers like "0" or "1"
        matches = re.findall(r'\b[01]\b', text)
        if matches:
            return float(matches[0])
        
        # Default: parse as is
        try:
            score = float(text)
            return min(max(score, 0.0), 1.0)
        except:
            # If parsing fails, return neutral score
            return 0.5
    
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
            return [
                {
                    'index': i,
                    'relevance_score': None,
                    'document': doc
                }
                for i, doc in enumerate(documents)
            ]
        
        results = []
        
        # Score each document
        for idx, doc in enumerate(documents):
            prompt = self._create_rerank_prompt(query, doc, idx)
            
            try:
                # Call completion endpoint
                payload = {
                    'prompt': prompt,
                    'temperature': 0.0,  # Deterministic
                    'max_tokens': 10,    # Just need a score
                    'stop': ['\n', 'Query:', 'Document:'],
                    'echo': False
                }
                
                response = requests.post(
                    self.api_url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract completion text
                if 'choices' in data and len(data['choices']) > 0:
                    completion_text = data['choices'][0].get('text', '0.5')
                    score = self._extract_score(completion_text)
                else:
                    score = 0.5  # Default score
                
                results.append({
                    'index': idx,
                    'relevance_score': score,
                    'document': doc
                })
                
            except Exception as e:
                print(f"[WARNING] Failed to rerank document {idx}: {e}")
                results.append({
                    'index': idx,
                    'relevance_score': 0.5,  # Neutral score on failure
                    'document': doc
                })
        
        # Sort by relevance score (descending)
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Return top_k if specified
        if top_k is not None:
            results = results[:top_k]
        
        return results
    
    def is_enabled(self) -> bool:
        """Check if reranker is enabled."""
        return self.enabled


if __name__ == "__main__":
    # Test the reranker
    print("Testing LlamaCpp Reranker Client\n")
    
    config = load_config()
    if not config.get('reranker', {}).get('enabled', False):
        print("Reranker is disabled in config")
        exit(0)
    
    try:
        client = LlamaCppRerankerClient()
        print(f"✓ Reranker client initialized")
        print(f"  API URL: {client.api_url}")
        print(f"  Model: {client.model_name}\n")
        
        # Test reranking
        query = "What is machine learning?"
        documents = [
            "Machine learning is a subset of AI that enables systems to learn from data.",
            "Python is a programming language popular for data science.",
            "Coffee is a popular beverage made from roasted beans."
        ]
        
        print(f"Query: {query}")
        print(f"Documents to rerank: {len(documents)}\n")
        
        results = client.rerank(query, documents)
        
        print("Reranked Results:")
        for i, result in enumerate(results, 1):
            print(f"  {i}. [Score: {result['relevance_score']:.4f}]")
            print(f"     {result['document'][:80]}")
            print()
        
    except Exception as e:
        print(f"✗ Error: {e}")
