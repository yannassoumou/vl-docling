# Qwen3VL RAG System - Project Overview

## What's New in Version 2.0

🎉 **Major Update**: Added flexible vector store support with both FAISS and Milvus!

### Key Enhancements

1. **Multiple Vector Store Support**
   - FAISS (local, fast, simple)
   - Milvus (scalable, production-ready)
   - Easy switching via configuration

2. **Flexible Configuration**
   - Environment variables (.env)
   - Command-line options (--store)
   - Programmatic configuration

3. **Production-Ready**
   - Docker Compose for Milvus
   - Automatic persistence with Milvus
   - Scalable to billions of vectors

## Project Structure

```
qwenvl/
├── Core Components
│   ├── embedding_client.py       # Qwen3VL API client
│   ├── document_processor.py     # Document chunking
│   ├── vector_store.py          # FAISS implementation
│   ├── milvus_store.py          # Milvus implementation
│   ├── vector_store_factory.py  # Factory pattern
│   ├── rag_engine.py            # Main RAG orchestrator
│   └── config.py                # Configuration
│
├── Applications
│   ├── main.py                  # CLI application
│   ├── example.py               # FAISS examples
│   ├── example_milvus.py        # Milvus examples
│   └── setup.py                 # Setup script
│
├── Configuration
│   ├── .env.example             # Environment template
│   ├── docker-compose.yml       # Milvus Docker setup
│   └── requirements.txt         # Python dependencies
│
├── Documentation
│   ├── README.md                # Main documentation
│   ├── GETTING_STARTED.md       # Quick decision guide
│   ├── QUICKSTART.md            # 5-minute tutorial
│   ├── MILVUS_SETUP.md          # Milvus setup guide
│   ├── VECTOR_STORES_GUIDE.md   # Detailed comparison
│   ├── CHANGELOG.md             # Version history
│   └── PROJECT_OVERVIEW.md      # This file
│
└── Sample Data
    └── sample_docs/             # Example documents
        ├── python_basics.txt
        ├── machine_learning.txt
        ├── neural_networks.txt
        └── rag_systems.txt
```

## Quick Start Guide

### For Beginners (FAISS)

```powershell
# 1. Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Run example
python example.py

# 3. Try CLI
python main.py ingest --directory ./sample_docs
python main.py query "What is Python?"
```

### For Production (Milvus)

```powershell
# 1. Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Start Milvus
docker-compose up -d

# 3. Configure
echo "VECTOR_STORE_TYPE=milvus" > .env

# 4. Run example
python example_milvus.py

# 5. Try CLI
python main.py ingest --directory ./sample_docs
python main.py query "What is machine learning?"
```

## Configuration Options

### Vector Store Selection

**Method 1: Environment Variable**
```bash
# .env file
VECTOR_STORE_TYPE=faiss  # or milvus
```

**Method 2: Command Line**
```powershell
python main.py --store milvus query "Your question"
```

**Method 3: Python Code**
```python
rag = RAGEngine(store_type='milvus')
```

### Milvus Configuration

```bash
# .env file
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION_NAME=rag_documents
MILVUS_INDEX_TYPE=IVF_FLAT
MILVUS_METRIC_TYPE=L2
```

## Feature Comparison

| Feature | FAISS | Milvus |
|---------|-------|--------|
| Setup | None | Docker/Server |
| Best For | Dev/Small | Production/Large |
| Max Documents | ~100K | Billions |
| Persistence | Manual | Automatic |
| Scalability | Single machine | Distributed |
| Speed | Very fast (local) | Fast (network) |

## Use Cases

### 1. Learning & Development
**Use FAISS**
- Zero setup
- Fast iteration
- Perfect for tutorials

### 2. Small Applications
**Use FAISS**
- < 100K documents
- Single server
- Simple deployment

### 3. Large Applications
**Use Milvus**
- > 100K documents
- Need scalability
- Production requirements

### 4. Multi-Tenant SaaS
**Use Milvus**
- Multiple collections
- Isolated data
- Scalable architecture

## API Overview

### Basic Usage

```python
from rag_engine import RAGEngine

# Initialize (FAISS default)
rag = RAGEngine()

# Or specify store
rag = RAGEngine(store_type='milvus')

# Ingest documents
rag.ingest_text("Your text", metadata={'source': 'doc.txt'})
rag.ingest_file("document.txt")
rag.ingest_directory("./docs")

# Query
result = rag.query("Your question?", top_k=5)
print(result['context'])

# Save (FAISS only, Milvus auto-saves)
rag.save()
```

### Advanced Usage

```python
# Custom configuration
rag = RAGEngine(
    store_type='milvus',
    host='remote-server.com',
    port='19530',
    user='admin',
    password='secret',
    collection_name='my_docs'
)

# Custom chunking
from document_processor import DocumentProcessor
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=100)
rag = RAGEngine(document_processor=processor)

# Get statistics
stats = rag.get_stats()
print(f"Total chunks: {stats['num_chunks']}")
print(f"Store type: {stats.get('store_type', 'faiss')}")
```

## CLI Commands

### Ingestion
```powershell
# Single file
python main.py ingest --file document.txt

# Directory
python main.py ingest --directory ./docs

# With file type filter
python main.py ingest --directory ./docs --extensions .txt .md

# Direct text
python main.py ingest --text "Your text here"

# With Milvus
python main.py --store milvus ingest --directory ./docs
```

### Querying
```powershell
# Basic query
python main.py query "What is Python?"

# More results
python main.py query "Explain ML" --top-k 10

# Context only (for LLM)
python main.py query "What is AI?" --context-only

# With Milvus
python main.py --store milvus query "Your question"
```

### Management
```powershell
# Statistics
python main.py stats

# Interactive mode
python main.py interactive

# Clear data
python main.py clear

# Help
python main.py --help
```

## Integration Examples

### With OpenAI
```python
import openai
from rag_engine import RAGEngine

rag = RAGEngine()
rag.load()

# Get context
context = rag.get_context("Your question", top_k=5)

# Generate answer
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"Answer based on:\n{context}"},
        {"role": "user", "content": "Your question"}
    ]
)
```

### With Ollama (Local LLM)
```python
import requests
from rag_engine import RAGEngine

rag = RAGEngine()
context = rag.get_context("Your question")

response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama2",
    "prompt": f"Context:\n{context}\n\nQuestion: Your question\n\nAnswer:"
})
```

## Documentation Guide

### Start Here
1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Choose your vector store
2. **[QUICKSTART.md](QUICKSTART.md)** - 5-minute tutorial

### Deep Dive
3. **[README.md](README.md)** - Complete documentation
4. **[VECTOR_STORES_GUIDE.md](VECTOR_STORES_GUIDE.md)** - Detailed comparison
5. **[MILVUS_SETUP.md](MILVUS_SETUP.md)** - Milvus setup (if needed)

### Reference
6. **[CHANGELOG.md](CHANGELOG.md)** - Version history
7. **[example.py](example.py)** - FAISS code examples
8. **[example_milvus.py](example_milvus.py)** - Milvus code examples

## Migration Guide

### From v1.0 to v2.0

**Good news**: Your existing code works without changes! FAISS remains the default.

**To use Milvus**:
```python
# Old (still works)
rag = RAGEngine()

# New (with Milvus)
rag = RAGEngine(store_type='milvus')
```

**To migrate data**:
```python
# Load from FAISS
rag_old = RAGEngine(store_type='faiss')
rag_old.load()

# Save to Milvus
rag_new = RAGEngine(store_type='milvus')
rag_new.vector_store.add_chunks(rag_old.vector_store.chunks)
```

## Performance Tips

### FAISS
- Keep datasets < 100K documents
- Use SSD for storage
- Save regularly
- Appropriate chunk size (300-500 chars)

### Milvus
- Choose right index type (HNSW for speed, IVF_PQ for scale)
- Use COSINE metric for text embeddings
- Batch insertions (default: 32)
- Monitor memory usage

## Troubleshooting

### Common Issues

**FAISS: File not found**
```python
rag = RAGEngine()
rag.ingest_text("Initial doc")
rag.save()
```

**Milvus: Connection failed**
```powershell
docker-compose ps  # Check status
docker-compose up -d  # Start if needed
```

**Milvus: Collection exists**
```python
rag = RAGEngine(store_type='milvus')
rag.clear()  # Clear existing
```

## Support & Resources

### Documentation
- Main: [README.md](README.md)
- Quick Start: [QUICKSTART.md](QUICKSTART.md)
- Milvus: [MILVUS_SETUP.md](MILVUS_SETUP.md)

### Examples
- FAISS: [example.py](example.py)
- Milvus: [example_milvus.py](example_milvus.py)

### External
- Milvus Docs: https://milvus.io/docs
- FAISS: https://github.com/facebookresearch/faiss
- Qwen: https://huggingface.co/Qwen

## What's Next?

### Roadmap Ideas
- [ ] Support for more vector stores (Pinecone, Weaviate, Qdrant)
- [ ] Built-in LLM integration
- [ ] Web UI for management
- [ ] Advanced filtering and metadata search
- [ ] Multi-modal support (images, audio)
- [ ] Hybrid search (vector + keyword)

## Summary

This RAG system now offers:
- ✅ **Flexibility**: Choose FAISS or Milvus
- ✅ **Scalability**: From prototype to production
- ✅ **Simplicity**: Easy configuration and usage
- ✅ **Production-Ready**: Docker, persistence, monitoring
- ✅ **Well-Documented**: Comprehensive guides and examples

**Start with FAISS for development, scale to Milvus for production!**

---

**Version**: 2.0.0  
**Last Updated**: 2026-01-16  
**License**: MIT
