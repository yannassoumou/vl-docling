import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
EMBEDDING_API_URL = os.getenv("EMBEDDING_API_URL", "http://100.126.235.19:8888/v1/embeddings")

# RAG Configuration
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks
TOP_K = 5  # number of documents to retrieve

# Vector Store Type: 'faiss' or 'milvus'
VECTOR_STORE_TYPE = os.getenv("VECTOR_STORE_TYPE", "faiss")

# FAISS Configuration
FAISS_STORE_PATH = "vector_store"
FAISS_INDEX_FILE = "faiss_index.bin"
FAISS_METADATA_FILE = "metadata.json"

# Milvus Configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
MILVUS_USER = os.getenv("MILVUS_USER", "")  # Optional authentication
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")  # Optional authentication
MILVUS_DB_NAME = os.getenv("MILVUS_DB_NAME", "default")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "rag_documents")
MILVUS_INDEX_TYPE = os.getenv("MILVUS_INDEX_TYPE", "IVF_FLAT")  # IVF_FLAT, HNSW, etc.
MILVUS_METRIC_TYPE = os.getenv("MILVUS_METRIC_TYPE", "L2")  # L2, IP, COSINE

# Legacy aliases for backward compatibility
VECTOR_STORE_PATH = FAISS_STORE_PATH
INDEX_FILE = FAISS_INDEX_FILE
METADATA_FILE = FAISS_METADATA_FILE
