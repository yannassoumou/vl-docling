# Vector Stores Configuration Guide

This guide explains how to configure and use different vector stores in the Qwen3VL RAG System.

## Overview

The RAG system supports two vector store backends:

1. **FAISS** - Fast local vector search library
2. **Milvus** - Scalable vector database (local or remote)

## Quick Comparison

| Feature | FAISS | Milvus |
|---------|-------|--------|
| **Setup Complexity** | None | Docker or Server |
| **Best For** | Development, Prototyping | Production, Scale |
| **Dataset Size** | < 100K documents | Unlimited |
| **Persistence** | Manual (save/load) | Automatic |
| **Scalability** | Single machine | Distributed |
| **Memory Usage** | All in-memory | Flexible |
| **Search Speed** | Very fast (local) | Fast (network overhead) |
| **Maintenance** | None | Server management |

## Configuration Methods

### Method 1: Environment Variables (.env file)

Create a `.env` file in the project root:

**For FAISS:**
```bash
VECTOR_STORE_TYPE=faiss
```

**For Local Milvus:**
```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=rag_documents
```

**For Remote Milvus:**
```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=your-server.example.com
MILVUS_PORT=19530
MILVUS_USER=your_username
MILVUS_PASSWORD=your_password
MILVUS_DB_NAME=production
MILVUS_COLLECTION_NAME=rag_documents
```

### Method 2: Command Line

Override the configuration for a single command:

```powershell
# Use FAISS
python main.py --store faiss ingest --directory ./docs

# Use Milvus
python main.py --store milvus query "What is Python?"
```

### Method 3: Python Code

```python
from rag_engine import RAGEngine

# FAISS (default)
rag = RAGEngine()

# Milvus (using config from .env)
rag = RAGEngine(store_type='milvus')

# Milvus with explicit configuration
rag = RAGEngine(
    store_type='milvus',
    host='remote-server.com',
    port='19530',
    user='admin',
    password='secret',
    collection_name='my_docs'
)
```

## FAISS Configuration

### Advantages
- ✅ Zero setup required
- ✅ Very fast for small datasets
- ✅ No external dependencies
- ✅ Perfect for development

### Disadvantages
- ❌ Manual persistence (must call `save()`)
- ❌ Limited to single machine
- ❌ All data must fit in memory
- ❌ No built-in replication

### Usage

```python
from rag_engine import RAGEngine

# Initialize
rag = RAGEngine(store_type='faiss')

# Load existing data
rag.load()

# Add documents
rag.ingest_directory('./docs')

# IMPORTANT: Save manually
rag.save()
```

### Storage Location

FAISS stores data in the `vector_store/` directory:
- `vector_store/faiss_index.bin` - Vector index
- `vector_store/metadata.json` - Document metadata

## Milvus Configuration

### Advantages
- ✅ Automatic persistence
- ✅ Scalable to billions of vectors
- ✅ Distributed architecture
- ✅ Multiple index types
- ✅ Production-ready

### Disadvantages
- ❌ Requires server setup
- ❌ More complex configuration
- ❌ Higher resource usage

### Setup

#### Option 1: Docker (Recommended)

```powershell
# Start Milvus
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f standalone

# Stop Milvus
docker-compose down
```

#### Option 2: Remote Server

Connect to an existing Milvus server:

```python
rag = RAGEngine(
    store_type='milvus',
    host='milvus.example.com',
    port='19530'
)
```

### Usage

```python
from rag_engine import RAGEngine

# Initialize
rag = RAGEngine(store_type='milvus')

# Load existing collection (if exists)
rag.load()

# Add documents
rag.ingest_directory('./docs')

# No need to call save() - Milvus persists automatically!
```

### Advanced Configuration

Edit `.env` for advanced settings:

```bash
# Index Type: FLAT, IVF_FLAT, IVF_SQ8, IVF_PQ, HNSW
MILVUS_INDEX_TYPE=IVF_FLAT

# Distance Metric: L2, IP (inner product), COSINE
MILVUS_METRIC_TYPE=L2

# Collection name (can have multiple collections)
MILVUS_COLLECTION_NAME=rag_documents
```

### Index Types

| Index | Speed | Accuracy | Memory | Best For |
|-------|-------|----------|--------|----------|
| FLAT | Slow | Perfect | High | < 10K vectors |
| IVF_FLAT | Fast | Good | Medium | 10K - 1M vectors |
| IVF_SQ8 | Fast | Good | Low | Memory constrained |
| HNSW | Very Fast | Excellent | High | Speed critical |
| IVF_PQ | Very Fast | Good | Very Low | > 1M vectors |

### Distance Metrics

| Metric | Use Case |
|--------|----------|
| L2 | General purpose, Euclidean distance |
| IP | Inner product, for normalized vectors |
| COSINE | Text embeddings, semantic similarity |

## Switching Between Stores

### Migrate from FAISS to Milvus

```python
from rag_engine import RAGEngine

# Load from FAISS
rag_faiss = RAGEngine(store_type='faiss')
rag_faiss.load()

# Get all chunks
chunks = rag_faiss.vector_store.chunks

# Create Milvus store and add chunks
rag_milvus = RAGEngine(store_type='milvus')
rag_milvus.vector_store.add_chunks(chunks)

print(f"Migrated {len(chunks)} chunks to Milvus")
```

### Migrate from Milvus to FAISS

```python
from rag_engine import RAGEngine

# Load from Milvus
rag_milvus = RAGEngine(store_type='milvus')
rag_milvus.load()

# Get chunks
chunks = rag_milvus.vector_store.chunks

# Create FAISS store and add chunks
rag_faiss = RAGEngine(store_type='faiss')
rag_faiss.vector_store.add_chunks(chunks)
rag_faiss.save()

print(f"Migrated {len(chunks)} chunks to FAISS")
```

## Use Case Recommendations

### Development & Prototyping
**Use FAISS**
```bash
VECTOR_STORE_TYPE=faiss
```
- Quick to start
- No setup needed
- Fast iteration

### Small Production (< 100K docs)
**Use FAISS**
```bash
VECTOR_STORE_TYPE=faiss
```
- Simple deployment
- Lower resource usage
- Sufficient performance

### Large Production (> 100K docs)
**Use Milvus**
```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=your-server.com
MILVUS_INDEX_TYPE=HNSW
MILVUS_METRIC_TYPE=COSINE
```
- Scalable
- Automatic persistence
- Production features

### Multi-Tenant Applications
**Use Milvus with Multiple Collections**
```python
# Tenant 1
rag1 = RAGEngine(store_type='milvus', collection_name='tenant_1_docs')

# Tenant 2
rag2 = RAGEngine(store_type='milvus', collection_name='tenant_2_docs')
```

## Troubleshooting

### FAISS Issues

**Problem: "No such file or directory: vector_store/faiss_index.bin"**
```python
# Solution: Initialize and save first
rag = RAGEngine(store_type='faiss')
rag.ingest_text("Initial document")
rag.save()
```

**Problem: Out of memory**
```python
# Solution: Use smaller chunks
from document_processor import DocumentProcessor
processor = DocumentProcessor(chunk_size=300)
rag = RAGEngine(document_processor=processor)
```

### Milvus Issues

**Problem: "Failed to connect to Milvus"**
```powershell
# Solution: Check if Milvus is running
docker-compose ps

# Start if not running
docker-compose up -d
```

**Problem: "Collection already exists"**
```python
# Solution 1: Use different collection name
rag = RAGEngine(store_type='milvus', collection_name='new_collection')

# Solution 2: Clear existing collection
rag = RAGEngine(store_type='milvus')
rag.clear()
```

**Problem: Slow queries**
```bash
# Solution: Use faster index
MILVUS_INDEX_TYPE=HNSW
```

## Performance Tips

### FAISS
1. Keep dataset size reasonable (< 100K documents)
2. Use appropriate chunk size (300-500 chars)
3. Save regularly to avoid data loss
4. Consider using SSD for storage

### Milvus
1. Choose appropriate index type for your dataset size
2. Use COSINE metric for text embeddings
3. Batch insertions (default: 32 chunks)
4. Monitor memory usage
5. Use HNSW for speed-critical applications

## Security

### FAISS
- Protect `vector_store/` directory
- Use file system permissions
- Encrypt at rest if needed

### Milvus
- Enable authentication:
  ```bash
  MILVUS_USER=admin
  MILVUS_PASSWORD=secure_password
  ```
- Use TLS for remote connections
- Implement network security (firewall, VPN)
- Regular backups

## Monitoring

### FAISS
```python
stats = rag.get_stats()
print(f"Chunks: {stats['num_chunks']}")
print(f"Dimension: {stats['dimension']}")
print(f"Sources: {stats['sources']}")
```

### Milvus
```python
stats = rag.get_stats()
print(f"Store type: {stats['store_type']}")
print(f"Host: {stats['host']}")
print(f"Collection: {stats['collection']}")
print(f"Chunks: {stats['num_chunks']}")
```

Or use Attu (Milvus GUI):
```powershell
docker run -p 8000:3000 -e MILVUS_URL=localhost:19530 zilliz/attu:latest
```

## Summary

- **Start with FAISS** for development and prototyping
- **Switch to Milvus** when you need scale or production features
- **Use .env file** for configuration management
- **Monitor performance** and adjust index types as needed
- **Regular backups** for FAISS, automatic for Milvus

For more details:
- FAISS: Built-in, no additional docs needed
- Milvus: See [MILVUS_SETUP.md](MILVUS_SETUP.md)
- General: See [README.md](README.md)
