# Milvus Vector Database Setup Guide

This guide explains how to set up and use Milvus as your vector database for the RAG system.

## What is Milvus?

Milvus is an open-source vector database built for scalable similarity search and AI applications. It offers:

- **Scalability**: Handle billions of vectors
- **Performance**: Millisecond search latency
- **Flexibility**: Multiple index types and distance metrics
- **Reliability**: Automatic persistence and replication
- **Production-Ready**: Used by many companies in production

## Comparison: FAISS vs Milvus

| Feature | FAISS | Milvus |
|---------|-------|--------|
| Setup | No setup needed | Requires server |
| Persistence | Manual save/load | Automatic |
| Scalability | Single machine | Distributed |
| Best for | Development, small datasets | Production, large datasets |
| Memory | All in-memory | Flexible |

## Installation Options

### Option 1: Local Milvus (Docker - Recommended)

The easiest way to run Milvus locally is using Docker.

#### Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- At least 4GB RAM available

#### Start Milvus Standalone

```powershell
# Download the docker-compose file
Invoke-WebRequest -Uri https://github.com/milvus-io/milvus/releases/download/v2.3.0/milvus-standalone-docker-compose.yml -OutFile docker-compose.yml

# Start Milvus
docker-compose up -d

# Check status
docker-compose ps
```

Milvus will be available at `localhost:19530`

#### Stop Milvus

```powershell
docker-compose down
```

#### Stop and delete data

```powershell
docker-compose down -v
```

### Option 2: Milvus Lite (Embedded)

For development, you can use Milvus Lite which runs in-process:

```powershell
pip install milvus
```

Then in your code:
```python
from milvus import default_server

# Start embedded Milvus
default_server.start()

# Your RAG code here
rag = RAGEngine(store_type='milvus', host='localhost', port='19530')

# Stop when done
default_server.stop()
```

### Option 3: Remote Milvus Server

For production, use a remote Milvus cluster or managed service:

- **Zilliz Cloud**: Fully managed Milvus (https://zilliz.com/cloud)
- **Self-hosted**: Deploy on Kubernetes or VMs

## Configuration

### Method 1: Using .env File (Recommended)

Create or edit `.env` file:

```bash
# Vector Store Type
VECTOR_STORE_TYPE=milvus

# Local Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_DB_NAME=default
MILVUS_COLLECTION_NAME=rag_documents

# Remote Milvus (example)
# MILVUS_HOST=your-server.com
# MILVUS_PORT=19530
# MILVUS_USER=admin
# MILVUS_PASSWORD=your_password

# Index Configuration
MILVUS_INDEX_TYPE=IVF_FLAT
MILVUS_METRIC_TYPE=L2
```

### Method 2: Command Line

```powershell
# Use Milvus for this session
python main.py --store milvus ingest --directory ./docs
python main.py --store milvus query "What is Python?"
```

### Method 3: Programmatic

```python
from rag_engine import RAGEngine

# Local Milvus
rag = RAGEngine(store_type='milvus')

# Remote Milvus
rag = RAGEngine(
    store_type='milvus',
    host='remote-server.com',
    port='19530',
    user='admin',
    password='secret',
    db_name='my_database',
    collection_name='my_collection'
)
```

## Quick Start with Milvus

### 1. Start Milvus (Docker)

```powershell
docker-compose up -d
```

Wait a few seconds for Milvus to start.

### 2. Configure the RAG System

Edit `.env`:
```
VECTOR_STORE_TYPE=milvus
```

### 3. Ingest Documents

```powershell
python main.py ingest --directory ./sample_docs
```

### 4. Query

```powershell
python main.py query "What is machine learning?"
```

That's it! Your data is now stored in Milvus.

## Advanced Configuration

### Index Types

Milvus supports multiple index types. Choose based on your needs:

| Index Type | Speed | Accuracy | Memory | Best For |
|------------|-------|----------|--------|----------|
| FLAT | Slow | Perfect | High | Small datasets (<10K) |
| IVF_FLAT | Fast | Good | Medium | Medium datasets (10K-1M) |
| IVF_SQ8 | Fast | Good | Low | Large datasets, memory constrained |
| HNSW | Very Fast | Excellent | High | Speed-critical applications |
| IVF_PQ | Very Fast | Good | Very Low | Very large datasets (>1M) |

Configure in `.env`:
```
MILVUS_INDEX_TYPE=HNSW  # For best speed
# or
MILVUS_INDEX_TYPE=IVF_PQ  # For best compression
```

### Distance Metrics

| Metric | Formula | Best For |
|--------|---------|----------|
| L2 | Euclidean distance | General purpose |
| IP | Inner Product | Normalized vectors |
| COSINE | Cosine similarity | Text embeddings |

Configure in `.env`:
```
MILVUS_METRIC_TYPE=COSINE  # Often best for text
```

## Monitoring and Management

### Using Python

```python
from pymilvus import connections, utility

# Connect
connections.connect(host='localhost', port='19530')

# List collections
collections = utility.list_collections()
print(f"Collections: {collections}")

# Get collection stats
from pymilvus import Collection
collection = Collection("rag_documents")
print(f"Total entities: {collection.num_entities}")

# Disconnect
connections.disconnect()
```

### Using Attu (GUI)

Attu is a web-based GUI for Milvus:

```powershell
docker run -p 8000:3000 -e MILVUS_URL=localhost:19530 zilliz/attu:latest
```

Then open http://localhost:8000 in your browser.

## Troubleshooting

### Connection Failed

```
Error: Failed to connect to Milvus: ...
```

**Solutions:**
1. Check if Milvus is running: `docker-compose ps`
2. Check the port: Default is 19530
3. Check firewall settings
4. For remote: Verify host/port are correct

### Out of Memory

```
Error: Cannot allocate memory
```

**Solutions:**
1. Use a more memory-efficient index: `IVF_SQ8` or `IVF_PQ`
2. Reduce batch size in config.py
3. Increase Docker memory limit
4. Use a machine with more RAM

### Collection Already Exists

```
Error: Collection already exists
```

**Solutions:**
1. Use a different collection name in `.env`
2. Or clear the collection: `python main.py clear`

### Slow Queries

**Solutions:**
1. Create an index: Milvus creates one automatically, but verify it exists
2. Use a faster index type: `HNSW`
3. Load collection into memory: `collection.load()`

## Migration from FAISS to Milvus

To migrate existing data from FAISS to Milvus:

```python
from rag_engine import RAGEngine

# Load from FAISS
rag_faiss = RAGEngine(store_type='faiss')
rag_faiss.load()

# Get chunks
chunks = rag_faiss.vector_store.chunks

# Save to Milvus
rag_milvus = RAGEngine(store_type='milvus')
rag_milvus.vector_store.add_chunks(chunks)

print(f"Migrated {len(chunks)} chunks to Milvus")
```

## Best Practices

### Development
- Use FAISS for quick prototyping
- Or use Milvus Lite for embedded testing

### Production
- Use Milvus Standalone or Cluster
- Enable authentication (user/password)
- Use appropriate index type for your data size
- Monitor memory usage
- Regular backups (Milvus handles persistence automatically)

### Performance Tuning
- Batch insertions (default: 32 chunks at a time)
- Choose index type based on dataset size
- Consider using `COSINE` metric for text embeddings
- Load collections into memory for faster queries

## Resources

- **Milvus Documentation**: https://milvus.io/docs
- **Milvus GitHub**: https://github.com/milvus-io/milvus
- **Zilliz Cloud** (Managed Milvus): https://zilliz.com/cloud
- **Community**: https://discord.gg/8uyFbECzPX

## Example Configuration Files

### Development (.env)

```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=dev_rag_docs
MILVUS_INDEX_TYPE=FLAT
```

### Production (.env)

```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=production-milvus.example.com
MILVUS_PORT=19530
MILVUS_USER=rag_app
MILVUS_PASSWORD=secure_password_here
MILVUS_DB_NAME=production
MILVUS_COLLECTION_NAME=rag_documents
MILVUS_INDEX_TYPE=HNSW
MILVUS_METRIC_TYPE=COSINE
```

---

Need help? Check the main [README.md](README.md) or open an issue on GitHub!
