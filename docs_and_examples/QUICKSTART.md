# Quick Start Guide

Get up and running with the Qwen3VL RAG System in 5 minutes!

## 🚀 Super Quick Start (Using Launcher Scripts)

**Windows PowerShell (Recommended):**
```powershell
# Just run this - it handles everything!
.\run.ps1 example
```

**Linux/Mac:**
```bash
# Make executable and run
chmod +x run.sh
./run.sh example
```

**That's it!** The launcher scripts automatically:
- Create virtual environment
- Install dependencies
- Run the example

See [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) for more options.

---

## 📋 Manual Setup (Alternative)

If you prefer manual control:

### Step 1: Setup (2 minutes)

```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

Or use the setup script:

```powershell
python setup.py
```

### Optional: Setup Milvus (for production)

If you want to use Milvus instead of FAISS:

```powershell
# Start Milvus with Docker
docker-compose up -d

# Configure in .env
echo "VECTOR_STORE_TYPE=milvus" > .env
```

See [MILVUS_SETUP.md](MILVUS_SETUP.md) for detailed instructions.

## Step 2: Ingest Documents (1 minute)

```powershell
# Ingest the sample documents
python main.py ingest --directory ./sample_docs
```

Expected output:
```
Starting ingestion...
Found 4 documents in ./sample_docs
Adding 16 chunks to vector store...
Successfully added 16 chunks. Total chunks: 16
Vector store saved to vector_store
Total chunks in system: 16
```

## Step 3: Query the System (1 minute)

```powershell
# Ask a question
python main.py query "What is Python?"
```

You'll see:
- The question
- Retrieved documents with relevance scores
- Source information
- Full context ready for an LLM

## Step 4: Try Interactive Mode (1 minute)

```powershell
python main.py interactive
```

Now you can ask multiple questions in a conversation!

Example queries to try:
- "What is machine learning?"
- "Explain neural networks"
- "How does RAG work?"
- "What are the benefits of Python?"

Type `exit` to quit.

## Next Steps

### Ingest Your Own Documents

```powershell
# Single file
python main.py ingest --file your_document.txt

# Entire directory
python main.py ingest --directory C:\path\to\your\docs

# Specific file types
python main.py ingest --directory ./docs --extensions .txt .md .py
```

### Use in Your Code

```python
from rag_engine import RAGEngine

# Initialize
rag = RAGEngine()
rag.load()

# Add documents
rag.ingest_text("Your content here")

# Query
result = rag.query("Your question?")
print(result['context'])

# Save
rag.save()
```

### Integration with LLMs

```python
# Get context for any LLM
context = rag.get_context("Your question", top_k=5)

# Use with OpenAI
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"Answer based on:\n{context}"},
        {"role": "user", "content": "Your question"}
    ]
)

# Or with local models (Ollama)
import requests
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "llama2",
    "prompt": f"Context:\n{context}\n\nQuestion: Your question"
})
```

## Troubleshooting

### Can't connect to API?

Test the connection:

```python
from embedding_client import QwenEmbeddingClient
client = QwenEmbeddingClient()
embedding = client.get_embeddings("test")
print(f"Success! Dimension: {embedding.shape}")
```

### No results from queries?

Check if you have documents:

```powershell
python main.py stats
```

If `Total chunks: 0`, you need to ingest documents first.

### Out of memory?

Use smaller chunks:

Edit `config.py`:
```python
CHUNK_SIZE = 300  # Smaller chunks
CHUNK_OVERLAP = 30
```

## Common Commands Reference

```powershell
# Ingest
python main.py ingest --file doc.txt
python main.py ingest --directory ./docs
python main.py ingest --text "Some text"

# Query
python main.py query "question"
python main.py query "question" --top-k 10
python main.py query "question" --context-only

# Manage
python main.py stats
python main.py clear
python main.py interactive

# Help
python main.py --help
python main.py ingest --help
```

## What's Next?

1. Read the full [README.md](README.md) for detailed documentation
2. Check out [example.py](example.py) for code examples
3. Customize [config.py](config.py) for your needs
4. Add your own documents and start building!

---

**Happy building! 🚀**
