# Launcher Scripts Guide

Easy-to-use scripts to run the RAG system on any platform!

## Available Scripts

### Main Launchers
- **`run.sh`** - Linux/Mac/WSL/Git Bash
- **`run.bat`** - Windows Command Prompt
- **`run.ps1`** - Windows PowerShell

### Milvus Setup
- **`setup-milvus.sh`** - Linux/Mac/WSL/Git Bash
- **`setup-milvus.bat`** - Windows Command Prompt
- **`setup-milvus.ps1`** - Windows PowerShell

## Quick Start

### Windows (PowerShell) - Recommended

```powershell
# Run interactive mode
.\run.ps1 interactive

# Ingest documents
.\run.ps1 ingest .\sample_docs

# Query
.\run.ps1 query "What is Python?"

# Run example
.\run.ps1 example

# Setup Milvus
.\setup-milvus.ps1
```

### Windows (Command Prompt)

```cmd
# Run interactive mode
run.bat interactive

# Ingest documents
run.bat ingest .\sample_docs

# Query
run.bat query "What is Python?"

# Run example
run.bat example

# Setup Milvus
setup-milvus.bat
```

### Linux/Mac/WSL

```bash
# Make scripts executable (first time only)
chmod +x run.sh setup-milvus.sh

# Run interactive mode
./run.sh interactive

# Ingest documents
./run.sh ingest ./sample_docs

# Query
./run.sh query "What is Python?"

# Run example
./run.sh example

# Setup Milvus
./setup-milvus.sh
```

## Features

### Automatic Setup
All launcher scripts automatically:
- ✅ Create virtual environment if needed
- ✅ Activate the virtual environment
- ✅ Install dependencies if missing
- ✅ Run your command

### No Manual Setup Required!
Just run the script and it handles everything.

## Commands Reference

### Interactive Mode
Start an interactive query session:

```powershell
# PowerShell
.\run.ps1 interactive

# Bash
./run.sh interactive

# Batch
run.bat interactive
```

### Ingest Documents

Ingest a directory:
```powershell
.\run.ps1 ingest .\sample_docs
.\run.ps1 ingest C:\Users\You\Documents
```

Ingest a single file:
```powershell
.\run.ps1 ingest .\document.txt
```

### Query the System

```powershell
.\run.ps1 query "What is machine learning?"
.\run.ps1 query "Explain Python programming"
```

### View Statistics

```powershell
.\run.ps1 stats
```

### Run Examples

FAISS example:
```powershell
.\run.ps1 example
```

Milvus example:
```powershell
.\run.ps1 example-milvus
```

### Setup Script

Run the interactive setup:
```powershell
.\run.ps1 setup
```

### Full Help

```powershell
.\run.ps1 help
```

### Advanced Usage

Pass any arguments directly to main.py:
```powershell
# Use Milvus
.\run.ps1 --store milvus query "Your question"

# Ingest with specific extensions
.\run.ps1 ingest --directory .\docs --extensions .txt .md

# Query with more results
.\run.ps1 query "Your question" --top-k 10

# Clear the database
.\run.ps1 clear
```

## Milvus Setup Scripts

### Quick Milvus Setup

The Milvus setup scripts automatically:
- ✅ Check Docker installation
- ✅ Start Milvus containers
- ✅ Wait for Milvus to be ready
- ✅ Provide next steps

### Windows PowerShell

```powershell
.\setup-milvus.ps1
```

### Windows Command Prompt

```cmd
setup-milvus.bat
```

### Linux/Mac/WSL

```bash
chmod +x setup-milvus.sh
./setup-milvus.sh
```

### After Milvus Setup

Configure the RAG system to use Milvus:

**PowerShell:**
```powershell
"VECTOR_STORE_TYPE=milvus" | Out-File .env -Encoding ASCII
```

**Command Prompt:**
```cmd
echo VECTOR_STORE_TYPE=milvus > .env
```

**Bash:**
```bash
echo "VECTOR_STORE_TYPE=milvus" > .env
```

Then use normally:
```powershell
.\run.ps1 ingest .\sample_docs
.\run.ps1 query "Your question"
```

## Platform-Specific Tips

### Windows PowerShell

**Execution Policy Issue?**

If you get "cannot be loaded because running scripts is disabled":

```powershell
# Allow scripts for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or run with bypass
powershell -ExecutionPolicy Bypass -File .\run.ps1 interactive
```

**Recommended:** Use PowerShell for best experience on Windows.

### Windows Command Prompt

Works out of the box, no special configuration needed.

```cmd
run.bat interactive
```

### Linux/Mac

**Make scripts executable (first time):**

```bash
chmod +x run.sh setup-milvus.sh
```

**Run with bash explicitly:**

```bash
bash run.sh interactive
```

### WSL (Windows Subsystem for Linux)

Use the Linux scripts:

```bash
chmod +x run.sh setup-milvus.sh
./run.sh interactive
```

### Git Bash on Windows

Use the Linux scripts:

```bash
chmod +x run.sh setup-milvus.sh
./run.sh interactive
```

## Examples

### Complete Workflow - PowerShell

```powershell
# 1. Run the example
.\run.ps1 example

# 2. Ingest your documents
.\run.ps1 ingest C:\Users\You\Documents

# 3. Query the system
.\run.ps1 query "What are the main topics?"

# 4. Interactive mode
.\run.ps1 interactive

# 5. Check statistics
.\run.ps1 stats
```

### Complete Workflow - Bash

```bash
# 1. Make executable (first time)
chmod +x run.sh

# 2. Run the example
./run.sh example

# 3. Ingest your documents
./run.sh ingest ~/Documents

# 4. Query the system
./run.sh query "What are the main topics?"

# 5. Interactive mode
./run.sh interactive

# 6. Check statistics
./run.sh stats
```

### Milvus Workflow - PowerShell

```powershell
# 1. Setup Milvus
.\setup-milvus.ps1

# 2. Configure
"VECTOR_STORE_TYPE=milvus" | Out-File .env -Encoding ASCII

# 3. Test with example
.\run.ps1 example-milvus

# 4. Use it
.\run.ps1 ingest .\sample_docs
.\run.ps1 interactive
```

## Troubleshooting

### "Permission denied" (Linux/Mac)

Make scripts executable:
```bash
chmod +x run.sh setup-milvus.sh
```

### "Script is not digitally signed" (PowerShell)

Allow scripts:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run with bypass:
```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 interactive
```

### "Python not found"

Install Python 3.8 or higher:
- Windows: https://www.python.org/downloads/windows/
- Mac: https://www.python.org/downloads/mac-osx/
- Linux: `sudo apt install python3 python3-pip python3-venv`

### "Docker not found" (Milvus setup)

Install Docker:
- Windows: https://docs.docker.com/desktop/install/windows-install/
- Mac: https://docs.docker.com/desktop/install/mac-install/
- Linux: https://docs.docker.com/engine/install/

### Virtual environment issues

Delete and recreate:

**PowerShell:**
```powershell
Remove-Item -Recurse -Force .venv
.\run.ps1 example
```

**Bash:**
```bash
rm -rf .venv
./run.sh example
```

## Summary

### Quick Reference Table

| Task | Windows (PS) | Windows (CMD) | Linux/Mac |
|------|-------------|---------------|-----------|
| Interactive | `.\run.ps1 interactive` | `run.bat interactive` | `./run.sh interactive` |
| Ingest | `.\run.ps1 ingest .\docs` | `run.bat ingest .\docs` | `./run.sh ingest ./docs` |
| Query | `.\run.ps1 query "Q?"` | `run.bat query "Q?"` | `./run.sh query "Q?"` |
| Example | `.\run.ps1 example` | `run.bat example` | `./run.sh example` |
| Stats | `.\run.ps1 stats` | `run.bat stats` | `./run.sh stats` |
| Setup Milvus | `.\setup-milvus.ps1` | `setup-milvus.bat` | `./setup-milvus.sh` |

### What the Scripts Do

1. **Check/create virtual environment** - No manual venv setup needed
2. **Activate virtual environment** - Automatically activated
3. **Install dependencies** - Only if missing
4. **Run your command** - Execute what you want

### No Setup Required!

Just download and run. The scripts handle everything.

---

**Need help?** See [README.md](README.md) or [QUICKSTART.md](QUICKSTART.md)
