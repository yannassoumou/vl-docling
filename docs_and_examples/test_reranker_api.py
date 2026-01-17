#!/usr/bin/env python3
"""
Test script for Qwen3-VL-Reranker API endpoints

Tests different endpoint formats to determine the best way to use the reranker.
"""

import requests
import json

SERVER_URL = "http://100.126.235.19:1111"

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

def print_test(test_name):
    """Print a test header."""
    print(f"\n{test_name}")
    print("-" * 80)

def test_rerank_endpoint():
    """Test 1: Native /v1/rerank endpoint."""
    print_test("Test 1: POST /v1/rerank (Native reranker endpoint)")
    
    url = f"{SERVER_URL}/v1/rerank"
    payload = {
        "model": "Qwen3-VL-Reranker-8B",
        "query": "What is machine learning?",
        "documents": [
            "Machine learning is a subset of AI that enables systems to learn from data.",
            "Python is a programming language popular for data science.",
            "Coffee is a popular beverage made from roasted beans."
        ]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"Response Body:\n{json.dumps(response.json(), indent=2)}")
            return True
        else:
            print(f"Response Body: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_completions_endpoint():
    """Test 2: /v1/completions endpoint with reranking prompt."""
    print_test("Test 2: POST /v1/completions (Using completion for reranking)")
    
    url = f"{SERVER_URL}/v1/completions"
    
    query = "What is machine learning?"
    document = "Machine learning is a subset of AI that enables systems to learn from data."
    
    prompt = f"""Query: {query}
Document: {document}

Rate the relevance of the document to the query on a scale from 0 to 1, where:
- 0 = completely irrelevant
- 1 = perfectly relevant

Relevance score:"""
    
    payload = {
        "prompt": prompt,
        "temperature": 0.0,
        "max_tokens": 10,
        "stop": ["\n", "Query:", "Document:"],
        "echo": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            
            # Extract the score
            if 'choices' in data and len(data['choices']) > 0:
                completion = data['choices'][0].get('text', '').strip()
                print(f"\n✓ Extracted completion: '{completion}'")
                return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat_completions_endpoint():
    """Test 3: /v1/chat/completions endpoint."""
    print_test("Test 3: POST /v1/chat/completions (Chat format for reranking)")
    
    url = f"{SERVER_URL}/v1/chat/completions"
    
    payload = {
        "model": "Qwen3-VL-Reranker-8B",
        "messages": [
            {
                "role": "system",
                "content": "You are a relevance scoring assistant. Rate document relevance to queries on a scale from 0 to 1."
            },
            {
                "role": "user",
                "content": "Query: What is machine learning?\nDocument: Machine learning is a subset of AI.\n\nRelevance score (0-1):"
            }
        ],
        "temperature": 0.0,
        "max_tokens": 10
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            
            # Extract the score
            if 'choices' in data and len(data['choices']) > 0:
                message = data['choices'][0].get('message', {})
                content = message.get('content', '').strip()
                print(f"\n✓ Extracted content: '{content}'")
                return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_models_endpoint():
    """Test 4: List available models."""
    print_test("Test 4: GET /v1/models (List available models)")
    
    url = f"{SERVER_URL}/v1/models"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response:\n{json.dumps(data, indent=2)}")
            return True
        else:
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health_endpoint():
    """Test 5: Check server health."""
    print_test("Test 5: GET /health (Server health)")
    
    url = f"{SERVER_URL}/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print_header("Testing Qwen3-VL-Reranker API Endpoints")
    print(f"Server URL: {SERVER_URL}")
    
    results = {}
    
    # Run tests
    results['rerank'] = test_rerank_endpoint()
    results['completions'] = test_completions_endpoint()
    results['chat_completions'] = test_chat_completions_endpoint()
    results['models'] = test_models_endpoint()
    results['health'] = test_health_endpoint()
    
    # Summary
    print_header("Test Summary")
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20s}: {status}")
    
    # Recommendation
    print("\n" + "=" * 80)
    print("RECOMMENDATION")
    print("=" * 80)
    
    if results['rerank']:
        print("✓ Use /v1/rerank endpoint (native reranker support)")
    elif results['chat_completions']:
        print("✓ Use /v1/chat/completions endpoint (chat-based reranking)")
    elif results['completions']:
        print("✓ Use /v1/completions endpoint (completion-based reranking)")
    else:
        print("✗ No working endpoint found for reranking")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
