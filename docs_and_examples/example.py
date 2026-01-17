#!/usr/bin/env python3
"""
Example usage of the Qwen3VL RAG System.

This script demonstrates how to use the RAG system programmatically.
"""

from rag_engine import RAGEngine, format_rag_response


def main():
    print("=" * 80)
    print("Qwen3VL RAG System - Example Usage")
    print("=" * 80)
    
    # Initialize the RAG engine
    print("\n1. Initializing RAG engine...")
    rag = RAGEngine()
    
    # Try to load existing data
    loaded = rag.load()
    if loaded:
        print("   ✓ Loaded existing vector store")
    else:
        print("   ✓ Created new RAG system")
    
    # Ingest sample documents
    print("\n2. Ingesting sample documents...")
    
    sample_docs = [
        {
            'text': """
            Python is a high-level, interpreted programming language known for its 
            simplicity and readability. It was created by Guido van Rossum and first 
            released in 1991. Python supports multiple programming paradigms including 
            procedural, object-oriented, and functional programming.
            """,
            'metadata': {'source': 'python_intro.txt', 'category': 'programming'}
        },
        {
            'text': """
            Machine Learning is a subset of artificial intelligence that enables 
            systems to learn and improve from experience without being explicitly 
            programmed. It focuses on the development of computer programs that can 
            access data and use it to learn for themselves.
            """,
            'metadata': {'source': 'ml_basics.txt', 'category': 'AI'}
        },
        {
            'text': """
            Deep Learning is a subset of machine learning that uses neural networks 
            with multiple layers. These neural networks attempt to simulate the 
            behavior of the human brain, allowing it to learn from large amounts 
            of data. Deep learning is behind many recent advances in AI.
            """,
            'metadata': {'source': 'deep_learning.txt', 'category': 'AI'}
        },
        {
            'text': """
            Natural Language Processing (NLP) is a branch of AI that helps computers 
            understand, interpret, and manipulate human language. NLP draws from many 
            disciplines including computer science and computational linguistics.
            """,
            'metadata': {'source': 'nlp_intro.txt', 'category': 'AI'}
        },
        {
            'text': """
            FAISS (Facebook AI Similarity Search) is a library for efficient similarity 
            search and clustering of dense vectors. It contains algorithms that search 
            in sets of vectors of any size, up to ones that possibly do not fit in RAM.
            """,
            'metadata': {'source': 'faiss_info.txt', 'category': 'tools'}
        }
    ]
    
    for doc in sample_docs:
        rag.ingest_text(doc['text'], metadata=doc['metadata'])
        print(f"   ✓ Ingested: {doc['metadata']['source']}")
    
    # Save the vector store
    print("\n3. Saving vector store...")
    rag.save()
    print("   ✓ Vector store saved")
    
    # Show statistics
    print("\n4. System Statistics:")
    stats = rag.get_stats()
    print(f"   - Total chunks: {stats['num_chunks']}")
    print(f"   - Embedding dimension: {stats['dimension']}")
    print(f"   - Number of sources: {len(stats['sources'])}")
    
    # Run some example queries
    print("\n5. Running example queries...")
    
    queries = [
        "What is Python?",
        "Explain machine learning",
        "What is FAISS used for?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'-' * 80}")
        print(f"Query {i}: {query}")
        print('-' * 80)
        
        result = rag.query(query, top_k=3)
        
        print(f"\nRetrieved {result['num_docs']} relevant documents:\n")
        for j, doc in enumerate(result['retrieved_docs'], 1):
            print(f"  {j}. {doc['metadata']['source']} (Score: {doc['score']:.4f})")
            print(f"     Category: {doc['metadata'].get('category', 'N/A')}")
            print(f"     Preview: {doc['content'][:100].strip()}...\n")
    
    # Example: Get context for LLM
    print("\n6. Getting context for LLM integration...")
    question = "What is the relationship between machine learning and deep learning?"
    context = rag.get_context(question, top_k=3)
    
    print(f"\nQuestion: {question}")
    print(f"\nContext length: {len(context)} characters")
    print("\nYou can now pass this context to an LLM API like:")
    print("- OpenAI GPT")
    print("- Anthropic Claude")
    print("- Local models via Ollama")
    print("\nTo generate an answer based on the retrieved context.")
    
    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
