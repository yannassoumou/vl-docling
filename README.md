# Qwen3VL RAG System

A complete Retrieval-Augmented Generation (RAG) application built on Qwen3VL embeddings. This system allows you to ingest documents, store them as vector embeddings, and retrieve relevant information using semantic search.

## Features

- 🚀 **Fast Vector Search**: Choose between FAISS (local) or Milvus (local/remote)
- 📊 **Multiple Vector Stores**: FAISS for quick development, Milvus for production scale
- 📄 **PDF Support with Visual Understanding**: Process PDFs page-by-page with both text and image embeddings
- 📊 **Office Document Support** ⭐ NEW!: Process PPTX (PowerPoint) and DOCX (Word) files
- 🖼️ **Multimodal Embeddings**: Leverage Qwen3-VL's ability to understand text, images, and combined inputs
- 🔍 **Semantic Retrieval**: Find relevant documents based on meaning, not just keywords
- 💾 **Persistent Storage**: Automatic persistence with Milvus, manual save/load with FAISS
- 🖥️ **CLI Interface**: Easy-to-use command-line interface with launcher scripts
- 🐍 **Python API**: Programmatic access for integration into your applications
- 🌐 **Qwen3VL Integration**: Uses the powerful [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B) model
- ⚙️ **Flexible Configuration**: Environment variables, config files, or command-line options

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENT INGESTION                            │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────┴───────────┐        │
        │                       │        │
┌───────▼───────┐   ┌───────▼───────┐   ┌───────▼───────┐
│  Text Files   │   │ Office Docs    │   │  PDF Files    │
│  (.txt, .md,  │   │ (.pptx, .docx)│   │  (.pdf)       │
│   .py, .js,   │   │ - Slides      │   │  - Multimodal │
│   .html, etc) │   │ - Paragraphs  │   │    processing │
└───────┬───────┘   │ - Tables      │   └───────┬───────┘
        │           └───────┬───────┘            │
        │                   │                    │
        │           ┌───────▼──────────────┐     │
        │           │  Office Processor    │     │
        │           │  (python-pptx/       │     │
        │           │   python-docx)       │     │
        │           │  - Text extraction   │     │
        │           └───────┬──────────────┘     │
        │                   │                    │
        │           ┌───────▼──────────────┐     │
        │           │  PDF Processor       │     │
        │           │  (Docling/Granite)   │     │
        │           │  - Page extraction   │     │
        │           │  - Text + Images     │     │
        │           └───────┬──────────────┘     │
        │                   │                    │
        └───────────┬───────┴────────────────────┘
                    │
        ┌───────────▼───────────┐
        │  Document Processor    │
        │  - Text chunking       │
        │  - Metadata extraction │
        └───────────┬───────────┘
                    │                   │
                    │           ┌───────▼──────────────┐
                    │           │  PDF Processor       │
                    │           │  (Docling/Granite)   │
                    │           │  - Page extraction   │
                    │           │  - Text + Images     │
                    │           └───────┬──────────────┘
                    │                   │
                    └───────────┬───────┘
                                │
                    ┌───────────▼───────────┐
                    │  Document Processor    │
                    │  - Text chunking       │
                    │  - Metadata extraction │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Qwen3VL Embedding    │
                    │  API Client           │
                    │  - Text embeddings    │
                    │  - Multimodal (text+  │
                    │    image) embeddings  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Vector Store Factory │
                    │  (Config-driven)      │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
            ┌───────▼───────┐       ┌───────▼───────┐
            │  FAISS Store  │       │ Milvus Store  │
            │  (Local)      │       │ (Local/Remote)│
            │  - Fast       │       │ - Scalable    │
            │  - Simple     │       │ - Persistent  │
            └───────┬───────┘       └───────┬───────┘
                    │                       │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │   Vector Database    │
                    │   (Embeddings Index)  │
                    └───────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                           QUERY PROCESSING                               │
└─────────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │   User Query           │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Qwen3VL Embedding    │
                    │  (Query → Embedding)  │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Vector Similarity    │
                    │  Search (Top-K)       │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Optional Reranker    │
                    │  (Two-stage retrieval)│
                    │  - Initial: Top 20    │
                    │  - Reranked: Top 5    │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Retrieved Context    │
                    │  - Documents          │
                    │  - Scores             │
                    │  - Metadata           │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  LLM Integration     │
                    │  (External)           │
                    │  - OpenAI             │
                    │  - Ollama             │
                    │  - Claude, etc.       │
                    └───────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         CONFIGURATION SYSTEM                             │
└─────────────────────────────────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
┌───────▼───────┐       ┌───────▼───────┐
│  config.yaml  │       │    .env       │
│  (YAML)       │       │  (Overrides)  │
└───────┬───────┘       └───────┬───────┘
        │                       │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │  Config Loader        │
        │  - Merges configs     │
        │  - Environment vars   │
        │  - CLI overrides      │
        └───────────────────────┘
```

### Key Components

1. **Document Processing**
   - **Text Files**: Direct chunking via `DocumentProcessor`
     - Supported: `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`, `.json`
     - Custom extensions can be specified
   - **Office Documents**: PPTX and DOCX support ⭐ NEW!
     - **PPTX**: Extracts text from all slides using `python-pptx`
     - **DOCX**: Extracts text from paragraphs and tables using `python-docx`
     - Both preserve document structure and metadata
   - **PDF Files**: Processed through Docling/Granite pipeline for text + image extraction
     - Multimodal processing with visual understanding
   - **Chunking**: Configurable chunk size and overlap

2. **Embedding Generation**
   - **Qwen3VL API**: Generates embeddings for text and multimodal (text+image) inputs
   - **Multimodal Support**: Handles both text-only and text+image chunks from PDFs

3. **Vector Storage**
   - **FAISS**: Fast local vector store, ideal for development
   - **Milvus**: Scalable vector database, production-ready with persistence
   - **Factory Pattern**: Automatic selection based on configuration

4. **Retrieval Pipeline**
   - **Stage 1**: Vector similarity search (fast, retrieves top-K candidates)
   - **Stage 2** (Optional): Reranker for improved relevance (re-ranks top candidates)
   - **Configurable**: Enable/disable reranker via config

5. **Configuration**
   - **YAML Config**: Main configuration file (`config.yaml`)
   - **Environment Variables**: Override via `.env` file
   - **CLI Options**: Command-line overrides for flexibility

## Installation

### 1. Set up Python Virtual Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Or for Windows Command Prompt
.\.venv\Scripts\activate.bat
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configuration

The system is pre-configured to use your embedding endpoint:

```
Endpoint: http://YOUR_TAILSCALE_IP:8888/v1/embeddings
Model: Qwen3-VL-Embedding-8B
```

#### Vector Store Selection

You can choose between two vector stores:

**FAISS (Default)** - Best for development and small datasets:
- No setup required
- Fast local search
- Good for < 100K documents

**Milvus** - Best for production and large datasets:
- Requires Milvus server (Docker recommended)
- Automatic persistence
- Scalable to billions of vectors
- See [MILVUS_SETUP.md](MILVUS_SETUP.md) for setup instructions

**Configure in `.env` file:**

```bash
# Use FAISS (default)
VECTOR_STORE_TYPE=faiss

# Or use Milvus
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

You can also modify other settings in `config.py` if needed.

## Quick Start

### Easy Way: Use Launcher Scripts (Recommended!)

We provide convenient launcher scripts for all platforms:

**Windows PowerShell:**
```powershell
.\run.ps1 example          # Run example
.\run.ps1 interactive      # Interactive mode
.\run.ps1 ingest .\docs    # Ingest documents
.\run.ps1 query "Question" # Query the system
```

**Windows Command Prompt:**
```cmd
run.bat example
run.bat interactive
run.bat ingest .\docs
```

**Linux/Mac/WSL:**
```bash
chmod +x run.sh            # Make executable (first time)
./run.sh example
./run.sh interactive
./run.sh ingest ./docs
```

**Benefits:**
- ✅ Automatic virtual environment setup
- ✅ Automatic dependency installation
- ✅ No manual activation needed
- ✅ Just run and go!

See [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) for complete documentation.

### Manual Way: Using Python Directly

### 1. Run the Example Script

```powershell
python example.py
```

This will:
- Initialize the RAG system
- Ingest sample documents
- Run example queries
- Show how to retrieve context

### 2. Using the CLI

#### Ingest Documents

```powershell
# Ingest a single file
python main.py ingest --file document.txt

# Ingest an entire directory
python main.py ingest --directory ./docs

# Ingest specific file types
python main.py ingest --directory ./docs --extensions .txt .md .py

# Ingest text directly
python main.py ingest --text "Your text here"

# Use Milvus instead of FAISS (override config)
python main.py --store milvus ingest --directory ./docs
```

#### Query the System

```powershell
# Basic query
python main.py query "What is machine learning?"

# Query with more results
python main.py query "Explain Python" --top-k 10

# Get only context (useful for piping to LLMs)
python main.py query "What is AI?" --context-only
```

#### Interactive Mode

```powershell
python main.py interactive
```

This starts an interactive session where you can ask multiple questions.

#### View Statistics

```powershell
python main.py stats
```

#### Clear Vector Store

```powershell
python main.py clear
```

## Python API Usage

### Using FAISS (Default)

```python
from rag_engine import RAGEngine

# Initialize the RAG engine (uses FAISS by default)
rag = RAGEngine()

# Load existing vector store (if available)
rag.load()

# Ingest documents
rag.ingest_text("Your text here", metadata={'source': 'my_doc.txt'})
rag.ingest_file("path/to/document.txt")
rag.ingest_directory("path/to/docs", extensions=['.txt', '.md'])

# Query the system
result = rag.query("What is Python?", top_k=5)

# Access results
print(f"Question: {result['question']}")
print(f"Found {result['num_docs']} relevant documents")

for doc in result['retrieved_docs']:
    print(f"Score: {doc['score']:.4f}")
    print(f"Content: {doc['content']}")
    print(f"Source: {doc['metadata']['source']}")

# Get context for LLM
context = rag.get_context("Explain machine learning", top_k=3)
# Pass this context to your LLM API

# Save the vector store
rag.save()

# Get statistics
stats = rag.get_stats()
print(f"Total chunks: {stats['num_chunks']}")
```

### Using Milvus

```python
from rag_engine import RAGEngine

# Initialize with local Milvus
rag = RAGEngine(store_type='milvus')

# Or with remote Milvus
rag = RAGEngine(
    store_type='milvus',
    host='remote-server.com',
    port='19530',
    user='admin',
    password='secret',
    collection_name='my_documents'
)

# Load existing collection
rag.load()

# Use the same API as FAISS
rag.ingest_directory("./docs")
result = rag.query("Your question?")

# Milvus automatically persists data
# No need to call save() manually
```

### Switching Between Stores

```python
# Use factory function for flexibility
from vector_store_factory import create_vector_store

# Create FAISS store
faiss_store = create_vector_store('faiss')

# Create Milvus store
milvus_store = create_vector_store('milvus', host='localhost')

# Use with RAG engine
rag = RAGEngine(vector_store=milvus_store)
```

## Configuration Options

### Environment Variables (.env)

```bash
# Embedding API
EMBEDDING_API_URL=http://YOUR_TAILSCALE_IP:8888/v1/embeddings

# Vector Store Type: 'faiss' or 'milvus'
VECTOR_STORE_TYPE=faiss

# Milvus Configuration (if using Milvus)
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=  # Optional
MILVUS_PASSWORD=  # Optional
MILVUS_DB_NAME=default
MILVUS_COLLECTION_NAME=rag_documents
MILVUS_INDEX_TYPE=IVF_FLAT
MILVUS_METRIC_TYPE=L2
```

### Python Configuration (config.py)

```python
# API Configuration
EMBEDDING_API_URL = "http://YOUR_TAILSCALE_IP:8888/v1/embeddings"

# Text Chunking
CHUNK_SIZE = 500  # characters per chunk
CHUNK_OVERLAP = 50  # overlap between chunks

# Retrieval
TOP_K = 5  # number of documents to retrieve by default

# Vector Store Type
VECTOR_STORE_TYPE = "faiss"  # or "milvus"
```

## Project Structure

```
qwenvl/
├── config.py                 # Configuration settings
├── embedding_client.py       # Qwen3VL API client
├── document_processor.py     # Document loading and chunking
├── vector_store.py          # FAISS vector store
├── milvus_store.py          # Milvus vector store
├── vector_store_factory.py  # Factory for creating stores
├── rag_engine.py            # Main RAG engine
├── main.py                  # CLI application
├── example.py               # Example usage
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── MILVUS_SETUP.md         # Milvus setup guide
├── QUICKSTART.md           # Quick start guide
├── sample_docs/            # Sample documents
└── vector_store/           # FAISS storage (created automatically)
    ├── faiss_index.bin
    └── metadata.json
```

## How It Works

### 1. Document Ingestion

Documents are processed in several steps:

1. **Loading**: Text files are loaded from disk or provided as strings
2. **Chunking**: Text is split into overlapping chunks (default: 500 chars with 50 char overlap)
3. **Embedding**: Each chunk is sent to the Qwen3VL API to generate embeddings
4. **Indexing**: Embeddings are stored in a FAISS index for fast similarity search

### 2. Query Processing

When you query the system:

1. **Query Embedding**: Your question is converted to an embedding using Qwen3VL
2. **Similarity Search**: FAISS finds the most similar document chunks
3. **Retrieval**: Relevant chunks are returned with similarity scores
4. **Context Building**: Retrieved chunks are formatted for use with LLMs

### 3. Integration with LLMs

The retrieved context can be passed to any LLM:

```python
# Get context
context = rag.get_context("Your question", top_k=5)

# Use with OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"Answer based on this context:\n{context}"},
        {"role": "user", "content": "Your question"}
    ]
)

# Or with local models via Ollama
import requests
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama2",
    "prompt": f"Context:\n{context}\n\nQuestion: Your question\n\nAnswer:"
})
```

## Advanced Usage

### Custom Chunking Strategy

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor(
    chunk_size=1000,  # Larger chunks
    chunk_overlap=100  # More overlap
)

rag = RAGEngine(document_processor=processor)
```

### Batch Processing

```python
# Process multiple files efficiently
import os

files = [f for f in os.listdir('docs') if f.endswith('.txt')]
for file in files:
    rag.ingest_file(os.path.join('docs', file))
    print(f"Processed: {file}")

rag.save()
```

### Filtering by Metadata

```python
# Add metadata during ingestion
rag.ingest_text("Technical content", metadata={
    'source': 'tech_doc.txt',
    'category': 'technical',
    'author': 'John Doe',
    'date': '2024-01-01'
})

# Retrieve and filter
results = rag.retrieve("your query", top_k=10)
technical_results = [r for r in results if r['metadata'].get('category') == 'technical']
```

## Troubleshooting

### Connection Issues

If you can't connect to the embedding API:

```python
# Test the connection
from embedding_client import QwenEmbeddingClient

client = QwenEmbeddingClient()
try:
    embedding = client.get_embeddings("test")
    print("Connection successful!")
    print(f"Embedding dimension: {embedding.shape}")
except Exception as e:
    print(f"Connection failed: {e}")
```

### Memory Issues

For large document sets:

```python
# Process in smaller batches
processor = DocumentProcessor(chunk_size=300)  # Smaller chunks
rag = RAGEngine(document_processor=processor)

# Add documents in batches
for i in range(0, len(documents), 100):
    batch = documents[i:i+100]
    for doc in batch:
        rag.ingest_file(doc)
    rag.save()  # Save after each batch
```

### Performance Optimization

```python
# Use smaller top_k for faster queries
results = rag.query("question", top_k=3)

# Reduce chunk size for faster ingestion
processor = DocumentProcessor(chunk_size=300, chunk_overlap=30)
```

## API Reference

### RAGEngine

- `ingest_text(text, metadata)`: Ingest a text string
- `ingest_file(file_path)`: Ingest a single file
- `ingest_directory(directory_path, extensions)`: Ingest a directory
- `retrieve(query, top_k)`: Retrieve relevant chunks
- `query(question, top_k)`: Full query with formatted results
- `get_context(query, top_k)`: Get concatenated context
- `save()`: Save vector store to disk
- `load()`: Load vector store from disk
- `clear()`: Clear vector store
- `get_stats()`: Get system statistics

### QwenEmbeddingClient

- `get_embeddings(texts)`: Get embeddings for text(s)
- `get_embedding_dimension()`: Get embedding vector dimension

### DocumentProcessor

- `load_text_file(file_path)`: Load a text file
- `load_directory(directory_path, extensions)`: Load directory
- `split_text(text)`: Split text into chunks
- `chunk_document(document)`: Chunk a single document
- `chunk_documents(documents)`: Chunk multiple documents

### VectorStore

- `add_chunks(chunks, batch_size)`: Add chunks to store
- `search(query, top_k)`: Search for similar chunks
- `save()`: Save index to disk
- `load()`: Load index from disk
- `clear()`: Clear the store
- `get_stats()`: Get statistics

## Contributing

Feel free to enhance this RAG system:

1. Add support for more document formats (PDF, DOCX, etc.)
2. Implement different chunking strategies
3. Add metadata filtering during retrieval
4. Integrate with different embedding models
5. Add support for multi-modal embeddings

## License

MIT License - Feel free to use and modify as needed.

## Choosing a Vector Store

### Use FAISS when:
- ✅ Developing and prototyping
- ✅ Small to medium datasets (< 100K documents)
- ✅ Single machine deployment
- ✅ No external dependencies desired
- ✅ Full control over storage location

### Use Milvus when:
- ✅ Production deployments
- ✅ Large datasets (> 100K documents)
- ✅ Need for scalability
- ✅ Multiple applications sharing data
- ✅ Automatic persistence required
- ✅ Advanced features (replication, sharding)

See [MILVUS_SETUP.md](MILVUS_SETUP.md) for detailed Milvus setup instructions.

## Acknowledgments

- Built with [FAISS](https://github.com/facebookresearch/faiss) for local vector search
- Built with [Milvus](https://milvus.io/) for scalable vector database
- Uses [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen) for embeddings
- Inspired by modern RAG architectures

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the example scripts
3. Test the embedding API connection
4. Check configuration settings

---

**Happy RAG-ing! 🚀**
