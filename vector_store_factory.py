"""
Vector Store Factory

Creates the appropriate vector store instance based on configuration.
"""

from typing import Union
from embedding_client import QwenEmbeddingClient
from vector_store import VectorStore
from milvus_store import MilvusStore
from config import VECTOR_STORE_TYPE


def create_vector_store(
    store_type: str = None,
    embedding_client: QwenEmbeddingClient = None,
    **kwargs
) -> Union[VectorStore, MilvusStore]:
    """
    Factory function to create a vector store instance.
    
    Args:
        store_type: Type of vector store ('faiss' or 'milvus'). 
                   If None, uses VECTOR_STORE_TYPE from config.
        embedding_client: Optional embedding client to use
        **kwargs: Additional arguments for the specific store
        
    Returns:
        VectorStore or MilvusStore instance
        
    Examples:
        # Create FAISS store
        store = create_vector_store('faiss')
        
        # Create local Milvus store
        store = create_vector_store('milvus')
        
        # Create remote Milvus store
        store = create_vector_store(
            'milvus',
            host='remote-server.com',
            port='19530',
            user='admin',
            password='password'
        )
    """
    store_type = (store_type or VECTOR_STORE_TYPE).lower()
    
    if store_type == 'faiss':
        return VectorStore(embedding_client=embedding_client, **kwargs)
    
    elif store_type == 'milvus':
        return MilvusStore(embedding_client=embedding_client, **kwargs)
    
    else:
        raise ValueError(
            f"Unknown vector store type: {store_type}. "
            f"Supported types: 'faiss', 'milvus'"
        )


def get_available_stores() -> dict:
    """
    Get information about available vector stores.
    
    Returns:
        Dictionary with store information
    """
    stores = {
        'faiss': {
            'name': 'FAISS',
            'description': 'Facebook AI Similarity Search - Local vector store',
            'pros': [
                'Fast local search',
                'No external dependencies',
                'Good for small to medium datasets'
            ],
            'cons': [
                'Limited to single machine',
                'No built-in persistence (manual save/load)',
                'Limited scalability'
            ]
        },
        'milvus': {
            'name': 'Milvus',
            'description': 'Open-source vector database - Local or remote',
            'pros': [
                'Scalable to billions of vectors',
                'Automatic persistence',
                'Distributed support',
                'Multiple index types',
                'Production-ready'
            ],
            'cons': [
                'Requires Milvus server',
                'More complex setup',
                'Higher resource usage'
            ]
        }
    }
    
    return stores


if __name__ == "__main__":
    # Display available stores
    print("Available Vector Stores:\n")
    
    stores = get_available_stores()
    for store_type, info in stores.items():
        print(f"=== {info['name']} ({store_type}) ===")
        print(f"Description: {info['description']}\n")
        print("Pros:")
        for pro in info['pros']:
            print(f"  + {pro}")
        print("\nCons:")
        for con in info['cons']:
            print(f"  - {con}")
        print("\n" + "-" * 60 + "\n")
    
    # Example usage
    print("Example Usage:\n")
    
    print("1. Using FAISS (default):")
    print("   store = create_vector_store('faiss')\n")
    
    print("2. Using local Milvus:")
    print("   store = create_vector_store('milvus')\n")
    
    print("3. Using remote Milvus:")
    print("   store = create_vector_store(")
    print("       'milvus',")
    print("       host='remote-server.com',")
    print("       port='19530',")
    print("       user='admin',")
    print("       password='password'")
    print("   )\n")
    
    print("4. Using environment variables (.env file):")
    print("   VECTOR_STORE_TYPE=milvus")
    print("   MILVUS_HOST=localhost")
    print("   MILVUS_PORT=19530")
    print("   store = create_vector_store()  # Uses config from .env")
