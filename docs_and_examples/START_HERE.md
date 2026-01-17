# 👋 START HERE - Qwen3VL RAG System

Welcome! This is your **one-page guide** to get started immediately.

## ⚡ 30-Second Quick Start

### Windows PowerShell (Copy & Paste):
```powershell
.\run.ps1 example
```

### Linux/Mac (Copy & Paste):
```bash
chmod +x run.sh && ./run.sh example
```

**That's it!** The script handles everything automatically.

---

## 📖 What is This?

A **complete RAG (Retrieval-Augmented Generation) system** that:

1. **Ingests your documents** → Breaks them into chunks
2. **Creates embeddings** → Using Qwen3VL model
3. **Stores in vector database** → FAISS or Milvus
4. **Retrieves relevant context** → When you ask questions
5. **Returns context** → Ready for LLM integration

## 🎯 What Can You Do?

### 1️⃣ Ask Questions About Your Documents
```powershell
# Add your documents
.\run.ps1 ingest C:\path\to\your\documents

# Ask questions
.\run.ps1 query "What are the main topics?"
```

### 2️⃣ Process PDFs with Visual Understanding ⭐ NEW!
```powershell
# Process PDFs (understands charts, diagrams, etc.)
.\run.ps1 example-pdf

# Add your PDFs
mkdir sample_pdfs
copy your-document.pdf sample_pdfs\
```

### 3️⃣ Interactive Chat Mode
```powershell
.\run.ps1 interactive
```
Type your questions and get instant answers!

### 4️⃣ Integrate with LLMs
```python
from rag_engine import RAGEngine

rag = RAGEngine()
context = rag.get_context("Your question")
# Pass context to ChatGPT, Claude, Ollama, etc.
```

## 🚀 Choose Your Path

### Path 1: Complete Beginner (5 minutes)
1. ✅ Run example: `.\run.ps1 example`
2. ✅ Try interactive: `.\run.ps1 interactive`
3. ✅ Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### Path 2: Quick User (10 minutes)
1. ✅ Read [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md)
2. ✅ Ingest your docs: `.\run.ps1 ingest .\your-docs`
3. ✅ Start using it!

### Path 3: Power User (30 minutes)
1. ✅ Read [README.md](README.md) - Full documentation
2. ✅ Read [GETTING_STARTED.md](GETTING_STARTED.md) - Choose FAISS or Milvus
3. ✅ Read [VECTOR_STORES_GUIDE.md](VECTOR_STORES_GUIDE.md) - Deep dive
4. ✅ Customize for your needs

## 📁 Available Scripts

### Main Launchers (Choose your platform)
- **`run.ps1`** - Windows PowerShell ⭐ Recommended for Windows
- **`run.bat`** - Windows Command Prompt
- **`run.sh`** - Linux/Mac/WSL/Git Bash

### Milvus Setup (For production scale)
- **`setup-milvus.ps1`** - Windows PowerShell
- **`setup-milvus.bat`** - Windows Command Prompt  
- **`setup-milvus.sh`** - Linux/Mac/WSL

## 📚 Documentation Map

```
START_HERE.md (You are here!)
│
├─ Quick & Simple
│  ├─ QUICK_REFERENCE.md      ← Cheat sheet
│  ├─ LAUNCHER_GUIDE.md        ← Script usage
│  └─ QUICKSTART.md            ← 5-min tutorial
│
├─ Understanding the System
│  ├─ PROJECT_OVERVIEW.md      ← What's included
│  ├─ GETTING_STARTED.md       ← Choose your setup
│  └─ README.md                ← Complete docs
│
└─ Advanced Topics
   ├─ VECTOR_STORES_GUIDE.md   ← FAISS vs Milvus
   ├─ MILVUS_SETUP.md          ← Production setup
   └─ CHANGELOG.md             ← Version history
```

## 🎓 Common Use Cases

### Use Case 1: Personal Knowledge Base
```powershell
# Add all your notes
.\run.ps1 ingest C:\Users\You\Documents\Notes

# Search through them
.\run.ps1 query "What did I write about Python?"
```

### Use Case 2: Research Assistant
```powershell
# Add research papers
.\run.ps1 ingest .\research-papers

# Interactive research
.\run.ps1 interactive
> Summarize the main findings
> What are the methodologies used?
> Compare the results across papers
```

### Use Case 3: Code Documentation Search
```powershell
# Index your codebase documentation
.\run.ps1 ingest .\project\docs --extensions .md .txt

# Find information
.\run.ps1 query "How do I configure the database?"
```

### Use Case 4: Customer Support Knowledge Base
```python
from rag_engine import RAGEngine

# Setup once
rag = RAGEngine()
rag.ingest_directory('./support-docs')
rag.save()

# Use in your app
def answer_customer_question(question):
    result = rag.query(question, top_k=5)
    context = result['context']
    # Pass to LLM for natural response
    return llm_generate(context, question)
```

## ⚙️ Two Vector Store Options

### Option 1: FAISS (Default)
**No setup required!** Just use it.

✅ Perfect for:
- Learning and testing
- Small to medium datasets (< 100K documents)
- Single machine deployment

```powershell
# It's already the default!
.\run.ps1 ingest .\docs
```

### Option 2: Milvus (Production)
**5-minute setup** for unlimited scale.

✅ Perfect for:
- Production applications
- Large datasets (> 100K documents)
- Multi-user applications

```powershell
# Setup once
.\setup-milvus.ps1

# Configure
"VECTOR_STORE_TYPE=milvus" | Out-File .env -Encoding ASCII

# Use it
.\run.ps1 ingest .\docs
```

## 🔥 Most Common Commands

| What You Want | Command |
|---------------|---------|
| **Run example** | `.\run.ps1 example` |
| **Add documents** | `.\run.ps1 ingest .\folder` |
| **Ask question** | `.\run.ps1 query "Question?"` |
| **Interactive mode** | `.\run.ps1 interactive` |
| **View stats** | `.\run.ps1 stats` |
| **Get help** | `.\run.ps1 help` |

## 💡 Pro Tips

### Tip 1: Start Simple
Use FAISS first (default). Switch to Milvus only when you need scale.

### Tip 2: Use Interactive Mode
Best for exploring your documents:
```powershell
.\run.ps1 interactive
```

### Tip 3: Integrate with LLMs
The RAG system provides context. Combine with ChatGPT/Claude/Ollama for answers:

```python
context = rag.get_context("Question", top_k=5)
answer = openai.chat("Use this context:\n" + context + "\n\nQuestion: ...")
```

### Tip 4: Check Statistics
See what's in your system:
```powershell
.\run.ps1 stats
```

## 🆘 Help & Troubleshooting

### "Permission denied" (Linux/Mac)
```bash
chmod +x run.sh setup-milvus.sh
```

### "Cannot load script" (PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Python not found"
Install Python 3.8+ from https://www.python.org/downloads/

### More Help
- **Quick answers**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Script help**: [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md)
- **Full docs**: [README.md](README.md)

## 🎯 Your Next Step

Choose one:

1. **Just Try It** (30 seconds)
   ```powershell
   .\run.ps1 example
   ```

2. **Learn More** (5 minutes)
   → Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

3. **Start Using** (10 minutes)
   ```powershell
   .\run.ps1 ingest .\your-documents
   .\run.ps1 interactive
   ```

---

## 📞 Quick Links

- 🚀 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheat sheet
- 📖 [LAUNCHER_GUIDE.md](LAUNCHER_GUIDE.md) - How to use scripts
- ⚡ [QUICKSTART.md](QUICKSTART.md) - 5-minute tutorial
- 📚 [README.md](README.md) - Complete documentation

---

## 🎉 You're Ready!

The system is designed to be **simple by default**, **powerful when needed**.

**Start with the basics:**
```powershell
.\run.ps1 example
```

**Then explore:**
- Add your own documents
- Try interactive mode
- Integrate with your application

**Need scale? Upgrade to Milvus:**
```powershell
.\setup-milvus.ps1
```

---

**Welcome aboard! 🚀**

Questions? Check the docs or just try the commands - they're designed to be self-explanatory.
