# Getting Started with Vector Store Configuration

This guide helps you choose and configure the right vector store for your needs.

## Quick Decision Tree

```
Do you need to handle > 100K documents?
├─ NO  → Use FAISS (default, no setup needed)
└─ YES → Use Milvus (requires Docker/server)

Is this for production?
├─ NO  → Use FAISS (simpler)
└─ YES → Use Milvus (more robust)

Do you need automatic persistence?
├─ NO  → Use FAISS (manual save/load)
└─ YES → Use Milvus (automatic)
```

## Option 1: FAISS (Recommended for Beginners)

### Setup (30 seconds)

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. That's it! FAISS is ready to use
python example.py
```

### Usage

```powershell
# Ingest documents
python main.py ingest --directory ./sample_docs

# Query
python main.py query "What is Python?"

# Interactive mode
python main.py interactive
```

### Pros & Cons

✅ **Pros:**
- Zero setup
- Very fast for small datasets
- Perfect for learning and development

❌ **Cons:**
- Must manually save data (`rag.save()`)
- Limited to single machine
- Not ideal for > 100K documents

## Option 2: Milvus (Recommended for Production)

### Setup (5 minutes)

```powershell
# 1. Start Milvus with Docker
docker-compose up -d

# 2. Wait 30 seconds for Milvus to start
Start-Sleep -Seconds 30

# 3. Configure
echo "VECTOR_STORE_TYPE=milvus" > .env

# 4. Test
python example_milvus.py
```

### Usage

```powershell
# Ingest documents (same commands, different backend)
python main.py ingest --directory ./sample_docs

# Query
python main.py query "What is machine learning?"

# Interactive mode
python main.py interactive
```

### Pros & Cons

✅ **Pros:**
- Automatic persistence
- Scalable to billions of vectors
- Production-ready
- Distributed support

❌ **Cons:**
- Requires Docker or server
- More complex setup
- Higher resource usage

## Configuration Cheat Sheet

### FAISS Configuration

**No configuration needed!** Just use it:

```python
from rag_engine import RAGEngine

rag = RAGEngine()  # Uses FAISS by default
rag.ingest_directory('./docs')
rag.save()  # Don't forget to save!
```

### Milvus Configuration

**Option A: Environment Variables (.env file)**

```bash
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=rag_documents
```

**Option B: Command Line**

```powershell
python main.py --store milvus ingest --directory ./docs
```

**Option C: Python Code**

```python
from rag_engine import RAGEngine

# Local Milvus
rag = RAGEngine(store_type='milvus')

# Remote Milvus
rag = RAGEngine(
    store_type='milvus',
    host='your-server.com',
    port='19530',
    user='admin',
    password='secret'
)
```

## Common Scenarios

### Scenario 1: Learning RAG Systems

**Use FAISS**

```powershell
# No setup needed
python example.py
python main.py ingest --directory ./sample_docs
python main.py interactive
```

### Scenario 2: Building a Prototype

**Use FAISS**

```python
from rag_engine import RAGEngine

rag = RAGEngine()
rag.ingest_directory('./my_docs')
rag.save()

result = rag.query("My question")
print(result['context'])
```

### Scenario 3: Small Production App (< 10K docs)

**Use FAISS**

```python
from rag_engine import RAGEngine

# Load existing data
rag = RAGEngine()
rag.load()

# Add new documents
rag.ingest_file('new_doc.txt')
rag.save()

# Query
result = rag.query(user_question)
```

### Scenario 4: Large Production App (> 100K docs)

**Use Milvus**

```powershell
# Setup once
docker-compose up -d
echo "VECTOR_STORE_TYPE=milvus" > .env

# Use in your app
```

```python
from rag_engine import RAGEngine

# Automatic persistence
rag = RAGEngine()
rag.load()

# Add documents (no need to call save!)
rag.ingest_directory('./docs')

# Query
result = rag.query(user_question)
```

### Scenario 5: Multi-Tenant Application

**Use Milvus with Multiple Collections**

```python
from rag_engine import RAGEngine

# Tenant 1
rag_tenant1 = RAGEngine(
    store_type='milvus',
    collection_name='tenant_1_docs'
)

# Tenant 2
rag_tenant2 = RAGEngine(
    store_type='milvus',
    collection_name='tenant_2_docs'
)
```

## Switching Between Stores

### Start with FAISS, Switch to Milvus Later

```python
# 1. Load from FAISS
from rag_engine import RAGEngine

rag_faiss = RAGEngine(store_type='faiss')
rag_faiss.load()

# 2. Get all chunks
chunks = rag_faiss.vector_store.chunks

# 3. Start Milvus
# docker-compose up -d

# 4. Create Milvus store and migrate
rag_milvus = RAGEngine(store_type='milvus')
rag_milvus.vector_store.add_chunks(chunks)

print(f"✓ Migrated {len(chunks)} chunks to Milvus")

# 5. Update .env
# VECTOR_STORE_TYPE=milvus
```

## Troubleshooting

### FAISS: "No such file"

```python
# Solution: Initialize first
rag = RAGEngine()
rag.ingest_text("Initial document")
rag.save()
```

### Milvus: "Connection failed"

```powershell
# Check if Milvus is running
docker-compose ps

# Start if needed
docker-compose up -d

# Wait for startup
Start-Sleep -Seconds 30

# Test connection
python example_milvus.py
```

### Milvus: "Collection already exists"

```python
# Option 1: Use different collection
rag = RAGEngine(
    store_type='milvus',
    collection_name='new_collection'
)

# Option 2: Clear existing
rag = RAGEngine(store_type='milvus')
rag.clear()
```

## Next Steps

### For FAISS Users
1. ✅ Read [QUICKSTART.md](QUICKSTART.md)
2. ✅ Try [example.py](example.py)
3. ✅ Ingest your documents
4. ✅ Build your application

### For Milvus Users
1. ✅ Read [MILVUS_SETUP.md](MILVUS_SETUP.md)
2. ✅ Start Milvus: `docker-compose up -d`
3. ✅ Try [example_milvus.py](example_milvus.py)
4. ✅ Configure via `.env` file
5. ✅ Build your application

### For Everyone
- 📖 [README.md](README.md) - Complete documentation
- 📖 [VECTOR_STORES_GUIDE.md](VECTOR_STORES_GUIDE.md) - Detailed comparison
- 📖 [QUICKSTART.md](QUICKSTART.md) - 5-minute tutorial
- 💻 [example.py](example.py) - FAISS examples
- 💻 [example_milvus.py](example_milvus.py) - Milvus examples

## Summary

| Need | Use | Setup Time | Command |
|------|-----|------------|---------|
| Learn RAG | FAISS | 0 min | `python example.py` |
| Prototype | FAISS | 0 min | `python main.py ingest --directory ./docs` |
| Small Prod | FAISS | 0 min | Same as above |
| Large Prod | Milvus | 5 min | `docker-compose up -d` |
| Multi-tenant | Milvus | 5 min | See Scenario 5 above |

**Default recommendation: Start with FAISS, migrate to Milvus when needed.**

---

Questions? Check the documentation or run:
```powershell
python main.py --help
python vector_store_factory.py  # See available stores
```
