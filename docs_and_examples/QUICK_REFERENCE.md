# Quick Reference Card

## 🚀 Getting Started in 30 Seconds

### Windows (PowerShell) - Copy & Paste This:

```powershell
# Run the example
.\run.ps1 example

# Try interactive mode
.\run.ps1 interactive
```

### Linux/Mac - Copy & Paste This:

```bash
# Make executable (first time only)
chmod +x run.sh

# Run the example
./run.sh example

# Try interactive mode
./run.sh interactive
```

## 📋 Common Commands Cheat Sheet

| What You Want | Windows PowerShell | Linux/Mac/WSL |
|---------------|-------------------|---------------|
| **Run Example** | `.\run.ps1 example` | `./run.sh example` |
| **PDF Example** ⭐ NEW! | `.\run.ps1 example-pdf` | `./run.sh example-pdf` |
| **Interactive Mode** | `.\run.ps1 interactive` | `./run.sh interactive` |
| **Add Documents** | `.\run.ps1 ingest .\folder` | `./run.sh ingest ./folder` |
| **Ask Question** | `.\run.ps1 query "Question?"` | `./run.sh query "Question?"` |
| **View Stats** | `.\run.ps1 stats` | `./run.sh stats` |
| **Get Help** | `.\run.ps1 help` | `./run.sh help` |

## 🗄️ Vector Store Selection

### FAISS (Default - No Setup)

**Use when:**
- Learning or prototyping
- < 100K documents
- Single machine

**No configuration needed!** Just use it.

### Milvus (Production Scale)

**Use when:**
- Production deployment
- > 100K documents
- Need scalability

**Setup:**
```powershell
# 1. Start Milvus
.\setup-milvus.ps1

# 2. Configure (PowerShell)
"VECTOR_STORE_TYPE=milvus" | Out-File .env -Encoding ASCII

# Or (Bash)
echo "VECTOR_STORE_TYPE=milvus" > .env

# 3. Use it
.\run.ps1 ingest .\docs
```

## 📝 Complete Workflow Example

### Windows PowerShell:
```powershell
# 1. Run example to test
.\run.ps1 example

# 2. Add your documents
.\run.ps1 ingest C:\Users\YourName\Documents

# 3. Ask questions
.\run.ps1 query "What is the main topic?"

# 4. Interactive session
.\run.ps1 interactive
  > What are the key points?
  > Summarize the documents
  > exit
```

### Linux/Mac:
```bash
# 1. Make executable (first time)
chmod +x run.sh

# 2. Run example
./run.sh example

# 3. Add your documents
./run.sh ingest ~/Documents

# 4. Ask questions
./run.sh query "What is the main topic?"

# 5. Interactive session
./run.sh interactive
```

## 🎯 Quick Decisions

### Which Script to Use?

```
Are you on Windows?
├─ Using PowerShell? → Use run.ps1 (recommended)
└─ Using Command Prompt? → Use run.bat

Are you on Linux/Mac?
└─ Use run.sh

Are you using WSL?
└─ Use run.sh

Are you using Git Bash on Windows?
└─ Use run.sh
```

### Which Vector Store?

```
How many documents?
├─ < 100K → Use FAISS (default, no setup)
└─ > 100K → Use Milvus (setup required)

Is this for production?
├─ No → Use FAISS
└─ Yes → Use Milvus
```

## 🔧 Troubleshooting

### PowerShell: "Cannot be loaded because running scripts is disabled"

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/Mac: "Permission denied"

```bash
chmod +x run.sh setup-milvus.sh
```

### "Python not found"

Install Python 3.8+ from https://www.python.org/downloads/

### Milvus: "Connection failed"

```powershell
# Check Docker is running
docker ps

# Start Milvus
.\setup-milvus.ps1
```

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) | Complete launcher scripts guide |
| [QUICKSTART.md](QUICKSTART.md) | 5-minute tutorial |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Choose your vector store |
| [README.md](README.md) | Full documentation |
| [MILVUS_SETUP.md](MILVUS_SETUP.md) | Milvus setup guide |

## 💡 Pro Tips

### Tip 1: Use Tab Completion
```powershell
# Type the start and press Tab
.\run<Tab>          # Completes to .\run.ps1
.\run.ps1 int<Tab>  # Completes to interactive
```

### Tip 2: Create Shortcuts
```powershell
# PowerShell: Create alias
Set-Alias rag ".\run.ps1"
rag interactive

# Bash: Create alias in ~/.bashrc
alias rag='./run.sh'
rag interactive
```

### Tip 3: Batch Operations
```powershell
# Ingest multiple directories
.\run.ps1 ingest .\docs1
.\run.ps1 ingest .\docs2
.\run.ps1 ingest .\docs3

# Then query
.\run.ps1 query "What's in all the docs?"
```

### Tip 4: Use with LLMs
```python
from rag_engine import RAGEngine

# Get context
rag = RAGEngine()
rag.load()
context = rag.get_context("Your question", top_k=5)

# Pass to ChatGPT, Claude, or local LLM
# The context is ready to use!
```

## 🎨 Visual Workflow

```
┌─────────────────┐
│  Your Documents │
└────────┬────────┘
         │
         │ .\run.ps1 ingest .\docs
         ▼
┌─────────────────┐
│   RAG System    │
│  (with Qwen3VL) │
└────────┬────────┘
         │
         │ .\run.ps1 query "Question?"
         ▼
┌─────────────────┐
│  Top 5 Results  │
│  + Context      │
└─────────────────┘
         │
         │ Pass to LLM (optional)
         ▼
┌─────────────────┐
│     Answer      │
└─────────────────┘
```

## 🚀 Advanced Usage

### Different Vector Stores
```powershell
# Force FAISS
.\run.ps1 --store faiss ingest .\docs

# Force Milvus
.\run.ps1 --store milvus query "Question?"
```

### Custom Options
```powershell
# More results
.\run.ps1 query "Question?" --top-k 10

# Specific file types
.\run.ps1 ingest --directory .\docs --extensions .txt .md .py

# Context only (for LLM)
.\run.ps1 query "Question?" --context-only
```

### Python API
```python
from rag_engine import RAGEngine

# Auto-setup and use
rag = RAGEngine()
rag.ingest_directory('./docs')
result = rag.query("Your question?")
print(result['context'])
```

---

## ⚡ One-Liners to Copy

### First Time Setup & Test
```powershell
# Windows PowerShell
.\run.ps1 example

# Linux/Mac
chmod +x run.sh && ./run.sh example
```

### Production with Milvus
```powershell
# Windows PowerShell
.\setup-milvus.ps1; "VECTOR_STORE_TYPE=milvus" | Out-File .env -Encoding ASCII; .\run.ps1 example-milvus

# Linux/Mac
./setup-milvus.sh && echo "VECTOR_STORE_TYPE=milvus" > .env && ./run.sh example-milvus
```

### Add All Docs and Query
```powershell
# Windows PowerShell
.\run.ps1 ingest .\sample_docs; .\run.ps1 query "What are the main topics?"

# Linux/Mac
./run.sh ingest ./sample_docs && ./run.sh query "What are the main topics?"
```

---

**Print this card and keep it handy!** 📄🖨️
