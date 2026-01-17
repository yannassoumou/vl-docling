#!/usr/bin/env python3
"""
Example usage of the Qwen3VL RAG System with Milvus.

This script demonstrates how to use Milvus as the vector store.
"""

from rag_engine import RAGEngine, format_rag_response


def main():
    print("=" * 80)
    print("Qwen3VL RAG System - Milvus Example")
    print("=" * 80)
    
    # Initialize the RAG engine with Milvus
    print("\n1. Initializing RAG engine with Milvus...")
    print("   Note: Make sure Milvus is running (e.g., via Docker)")
    print("   See MILVUS_SETUP.md for setup instructions\n")
    
    try:
        # Local Milvus
        rag = RAGEngine(store_type='milvus')
        
        # For remote Milvus, use:
        # rag = RAGEngine(
        #     store_type='milvus',
        #     host='remote-server.com',
        #     port='19530',
        #     user='admin',
        #     password='password'
        # )
        
        print("   ✓ Connected to Milvus")
    except Exception as e:
        print(f"   ✗ Failed to connect to Milvus: {e}")
        print("\n   Please ensure Milvus is running:")
        print("   docker-compose up -d")
        print("\n   Or see MILVUS_SETUP.md for setup instructions")
        return
    
    # Try to load existing data
    loaded = rag.load()
    if loaded:
        print("   ✓ Loaded existing collection")
    else:
        print("   ✓ Created new collection")
    
    # Ingest sample documents
    print("\n2. Ingesting sample documents...")
    
    sample_docs = [
        {
            'text': """
            Milvus is an open-source vector database built to power embedding similarity 
            search and AI applications. It makes unstructured data search more accessible 
            and provides a consistent user experience regardless of the deployment environment.
            """,
            'metadata': {'source': 'milvus_intro.txt', 'category': 'database'}
        },
        {
            'text': """
            Vector databases are specialized databases designed to store and query 
            high-dimensional vectors efficiently. They are essential for modern AI 
            applications like semantic search, recommendation systems, and RAG.
            """,
            'metadata': {'source': 'vector_db.txt', 'category': 'database'}
        },
        {
            'text': """
            FAISS (Facebook AI Similarity Search) is a library for efficient similarity 
            search and clustering of dense vectors. It's great for prototyping and 
            small-scale applications but lacks the scalability of dedicated vector databases.
            """,
            'metadata': {'source': 'faiss_info.txt', 'category': 'tools'}
        },
        {
            'text': """
            Retrieval-Augmented Generation (RAG) combines the power of large language 
            models with external knowledge retrieval. Vector databases play a crucial 
            role in RAG by enabling fast and accurate retrieval of relevant context.
            """,
            'metadata': {'source': 'rag_overview.txt', 'category': 'AI'}
        }
    ]
    
    for doc in sample_docs:
        rag.ingest_text(doc['text'], metadata=doc['metadata'])
        print(f"   ✓ Ingested: {doc['metadata']['source']}")
    
    # Note: Milvus automatically persists data
    print("\n3. Data persistence:")
    print("   ✓ Milvus automatically persists data to disk")
    print("   ✓ No need to manually call save()")
    
    # Show statistics
    print("\n4. System Statistics:")
    stats = rag.get_stats()
    print(f"   - Store type: {stats.get('store_type', 'N/A')}")
    print(f"   - Total chunks: {stats['num_chunks']}")
    print(f"   - Embedding dimension: {stats['dimension']}")
    print(f"   - Milvus host: {stats.get('host', 'N/A')}")
    print(f"   - Collection: {stats.get('collection', 'N/A')}")
    
    # Run some example queries
    print("\n5. Running example queries...")
    
    queries = [
        "What is Milvus?",
        "Explain vector databases",
        "How does RAG use vector databases?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'-' * 80}")
        print(f"Query {i}: {query}")
        print('-' * 80)
        
        result = rag.query(query, top_k=2)
        
        print(f"\nRetrieved {result['num_docs']} relevant documents:\n")
        for j, doc in enumerate(result['retrieved_docs'], 1):
            print(f"  {j}. {doc['metadata']['source']} (Score: {doc['score']:.4f})")
            print(f"     Category: {doc['metadata'].get('category', 'N/A')}")
            print(f"     Preview: {doc['content'][:100].strip()}...\n")
    
    # Demonstrate Milvus advantages
    print("\n6. Milvus Advantages:")
    print("   ✓ Automatic persistence - data survives restarts")
    print("   ✓ Scalable - can handle billions of vectors")
    print("   ✓ Distributed - supports clustering for high availability")
    print("   ✓ Multiple indexes - IVF_FLAT, HNSW, IVF_PQ, etc.")
    print("   ✓ Production-ready - used by many companies")
    
    print("\n7. Comparison with FAISS:")
    print("   FAISS:")
    print("   - Good for: Development, small datasets")
    print("   - Pros: No setup, fast local search")
    print("   - Cons: Manual persistence, limited scalability")
    print("\n   Milvus:")
    print("   - Good for: Production, large datasets")
    print("   - Pros: Auto persistence, scalable, distributed")
    print("   - Cons: Requires server setup")
    
    print("\n" + "=" * 80)
    print("Milvus example completed successfully!")
    print("=" * 80)
    
    print("\nNext steps:")
    print("  1. Try the CLI with Milvus:")
    print("     python main.py --store milvus query 'Your question'")
    print("\n  2. Configure via .env file:")
    print("     VECTOR_STORE_TYPE=milvus")
    print("\n  3. See MILVUS_SETUP.md for advanced configuration")


if __name__ == "__main__":
    main()
