# Document Ingestion Guide

## Recursive Ingestion (Default)

By default, **all ingest commands process ALL files and subfolders recursively**! ✅

## Examples

### ✅ Recursive (Default) - Processes ALL subfolders

```powershell
# Ingest entire directory tree
.\run.ps1 ingest --directory .\my_documents

# This will process:
# my_documents/file1.txt
# my_documents/subfolder/file2.txt
# my_documents/subfolder/deep/file3.txt
# ... and so on!
```

**Output:**
```
Scanning directory (recursive)...
  Scanning: subfolder1/
    ✓ subfolder1/document.txt
  Scanning: subfolder2/
    ✓ subfolder2/file.md
    ✓ subfolder2/data.json
Found 15 documents in ./my_documents (including subdirectories)
```

### Non-Recursive - Only top-level files

```powershell
# Only process files in the main directory
.\run.ps1 ingest --directory .\my_documents --no-recursive

# This will ONLY process:
# my_documents/file1.txt
# my_documents/file2.txt
# (ignores subfolders)
```

## Supported File Types

By default, these extensions are processed:
- `.txt` - Text files
- `.md` - Markdown
- `.py` - Python
- `.js` - JavaScript
- `.html` - HTML
- `.css` - CSS
- `.json` - JSON
- `.pdf` - PDF (multimodal)

### Custom Extensions

```powershell
# Only process specific file types
.\run.ps1 ingest --directory .\docs --extensions .txt .md

# Process code files only
.\run.ps1 ingest --directory .\src --extensions .py .js .java
```

## PDF Processing

PDFs are also processed recursively by default:

```powershell
# Process all PDFs in directory tree
.\run.ps1 ingest --directory .\research_papers

# Shows progress:
# Scanning for PDFs (recursive)...
# Found 25 PDF file(s)
# 
# [1/25] Processing: folder1/paper1.pdf
#   Processing PDF: folder1/paper1.pdf
#   Extracted 10 pages
#   ✓ Completed: 10 pages
# 
# [2/25] Processing: folder2/paper2.pdf
# ...
```

## Command Reference

### Basic Ingestion

```powershell
# Single file
.\run.ps1 ingest --file document.txt

# Directory (recursive - ALL subfolders)
.\run.ps1 ingest --directory .\documents

# Directory (non-recursive - top-level only)
.\run.ps1 ingest --directory .\documents --no-recursive

# Direct text
.\run.ps1 ingest --text "Your text here"
```

### With Options

```powershell
# Custom file types
.\run.ps1 ingest --directory .\docs --extensions .txt .md .pdf

# Non-recursive with custom types
.\run.ps1 ingest --directory .\docs --extensions .txt --no-recursive

# Use Milvus instead of FAISS
.\run.ps1 --store milvus ingest --directory .\large_dataset
```

## Python API

### Recursive (Default)

```python
from rag_engine import RAGEngine

rag = RAGEngine()

# Processes ALL subdirectories (default)
rag.ingest_directory('./documents')

# Explicit recursive
rag.ingest_directory('./documents', recursive=True)
```

### Non-Recursive

```python
# Only top-level files
rag.ingest_directory('./documents', recursive=False)
```

### With Custom Extensions

```python
# Only specific file types
rag.ingest_directory('./docs', extensions=['.txt', '.md'])

# Recursive with custom types
rag.ingest_directory('./docs', extensions=['.py', '.js'], recursive=True)
```

### PDF Processing

```python
from multimodal_rag import MultimodalRAGEngine

rag = MultimodalRAGEngine()

# Process all PDFs recursively (default)
rag.ingest_pdf_directory('./research', mode='multimodal')

# Non-recursive
rag.ingest_pdf_directory('./research', recursive=False)
```

## Typical Directory Structures

### Example 1: Documentation

```
docs/
├── getting-started.md
├── api/
│   ├── authentication.md
│   ├── endpoints.md
│   └── examples/
│       ├── example1.md
│       └── example2.md
└── guides/
    ├── tutorial1.md
    └── tutorial2.md
```

**Command:**
```powershell
.\run.ps1 ingest --directory .\docs
```

**Result:** ✅ ALL 7 files processed (including subdirectories)

### Example 2: Code Repository

```
src/
├── main.py
├── utils/
│   ├── helpers.py
│   └── validators.py
├── api/
│   └── routes.py
└── tests/
    └── test_main.py
```

**Command:**
```powershell
.\run.ps1 ingest --directory .\src --extensions .py
```

**Result:** ✅ ALL 5 Python files processed

### Example 3: Mixed Content

```
project/
├── README.md
├── docs/
│   └── manual.pdf
├── code/
│   └── app.py
└── data/
    └── info.txt
```

**Command:**
```powershell
# All files (text + PDF)
.\run.ps1 ingest --directory .\project

# Only markdown and Python
.\run.ps1 ingest --directory .\project --extensions .md .py
```

## Progress Feedback

The system shows detailed progress:

```
Scanning directory (recursive)...
  Scanning: subfolder1/
    ✓ subfolder1/doc1.txt
    ✓ subfolder1/doc2.md
  Scanning: subfolder2/
    ✓ subfolder2/file.txt
  Scanning: subfolder2/deep/
    ✓ subfolder2/deep/nested.txt
Found 4 documents in ./my_documents (including subdirectories)
Adding 4 chunks to vector store...
Generating embeddings: 100%|████████| 1/1 [00:01<00:00]
Successfully added 4 chunks. Total chunks: 4
✓ Successfully ingested directory: ./my_documents
```

## Tips

### 1. Start with a Small Test

```powershell
# Test with one subdirectory first
.\run.ps1 ingest --directory .\docs\getting-started

# Then process the full tree
.\run.ps1 ingest --directory .\docs
```

### 2. Filter by File Type

```powershell
# Only documentation
.\run.ps1 ingest --directory .\project --extensions .md .txt

# Only code
.\run.ps1 ingest --directory .\project --extensions .py .js .java
```

### 3. Check What Will Be Processed

Use your file explorer or command line to see the structure:

```powershell
# Windows PowerShell
Get-ChildItem -Recurse -Filter *.txt

# Linux/Mac
find . -name "*.txt"
```

### 4. Large Datasets

For large directory trees:

```powershell
# Use Milvus for better performance
.\run.ps1 --store milvus ingest --directory .\large_dataset

# Or process in batches
.\run.ps1 ingest --directory .\large_dataset\batch1
.\run.ps1 ingest --directory .\large_dataset\batch2
```

## Summary

✅ **Recursive by default** - Processes all subfolders automatically  
✅ **Clear progress** - Shows which files are being processed  
✅ **Flexible filtering** - Choose specific file types  
✅ **Non-recursive option** - Add `--no-recursive` if needed  
✅ **Works for all file types** - Text, code, PDFs, etc.  

**Just run:**
```powershell
.\run.ps1 ingest --directory .\your_folder
```

**And watch it process everything! 🚀**
