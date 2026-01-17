# PDF Processing with Multimodal RAG

## Overview

This RAG system now supports **PDF processing with visual understanding** powered by [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B).

### Why Multimodal?

Traditional RAG systems only use extracted text from PDFs, missing important visual information like:
- 📊 Charts and graphs
- 📈 Diagrams and flowcharts
- 🖼️ Images and screenshots
- 📐 Tables with complex formatting
- ✍️ Handwritten notes or annotations

**Qwen3-VL-Embedding** understands both text AND visual content, making your RAG system much more powerful!

## How It Works

```
PDF Document
     │
     ├─► Page 1 ──► [Text Extraction] ──┐
     │             [Image Rendering]    ├─► Multimodal Embedding
     │                                   │
     ├─► Page 2 ──► [Text + Image] ─────┤
     │                                   │
     └─► Page N ──► [Text + Image] ─────┘
                                         │
                                         ▼
                                   Vector Store
                                         │
                                         │ Query
                                         ▼
                              Retrieved Context
                           (Text + Page Images)
```

Each PDF page is converted to:
1. **Extracted text** - All text content from the page
2. **Page image** - Visual rendering at 150 DPI (configurable)

Both are embedded together using Qwen3-VL's multimodal capabilities.

## Quick Start

### 1. Install Dependencies

```powershell
# Windows PowerShell
.\run.ps1 example-pdf

# Linux/Mac
./run.sh example-pdf
```

The launcher automatically installs required dependencies:
- `PyMuPDF` - PDF processing
- `Pillow` - Image handling

### 2. Add Your PDFs

Create a `sample_pdfs/` directory and add your PDF files:

```powershell
# Create directory
mkdir sample_pdfs

# Add your PDFs
copy your-document.pdf sample_pdfs\
```

### 3. Run the Example

```powershell
# Windows PowerShell
.\run.ps1 example-pdf

# Linux/Mac
./run.sh example-pdf
```

## Programmatic Usage

### Basic PDF Processing

```python
from multimodal_rag import MultimodalRAGEngine

# Initialize engine
rag = MultimodalRAGEngine()

# Process a PDF (multimodal: text + images)
rag.ingest_pdf('document.pdf', mode='multimodal')

# Query the system
result = rag.query("What information is shown in the charts?")

# Access results
for chunk in result['retrieved_chunks']:
    print(f"Page {chunk['metadata']['page_number']}")
    print(f"Text: {chunk['text'][:200]}")
    print(f"Has image: {chunk['has_image']}")
    
    # Display or save the page image
    if chunk['image']:
        chunk['image'].show()
        # or chunk['image'].save(f"page_{chunk['metadata']['page_number']}.png")
```

### Processing Modes

```python
# Multimodal: Text + Images (recommended)
rag.ingest_pdf('doc.pdf', mode='multimodal')

# Text-only: Just extracted text
rag.ingest_pdf('doc.pdf', mode='text-only')

# Image-only: Just page images
rag.ingest_pdf('doc.pdf', mode='image-only')
```

### Process Specific Pages

```python
# Process only pages 1, 2, and 5
rag.ingest_pdf('document.pdf', pages=[1, 2, 5])

# Process page range
pages = list(range(10, 20))  # Pages 10-19
rag.ingest_pdf('document.pdf', pages=pages)
```

### Process Directory of PDFs

```python
# Process all PDFs in a directory
rag.ingest_pdf_directory('./documents', mode='multimodal')

# Non-recursive (only top level)
rag.ingest_pdf_directory('./documents', recursive=False)
```

### Custom DPI Settings

```python
# Higher DPI = better quality, larger files
rag = MultimodalRAGEngine(pdf_dpi=300)  # High quality

# Lower DPI = faster processing, smaller files  
rag = MultimodalRAGEngine(pdf_dpi=100)  # Fast processing
```

### Query with Visual Context

```python
# Query normally
result = rag.query("What is the revenue trend?")

# Query with an image (comparing with retrieved images)
from PIL import Image
query_img = Image.open('similar_chart.jpg')
result = rag.query("Find similar charts", question_image=query_img)
```

## Advanced Usage

### Custom PDF Processing

```python
from pdf_processor import PDFProcessor, pdf_page_to_multimodal_document

# Create custom processor
processor = PDFProcessor(
    dpi=200,  # Custom resolution
    extract_text=True,
    image_format='PNG'
)

# Process PDF
pages = processor.process_pdf('document.pdf')

# Access page data
for page in pages:
    print(f"Page {page.page_number}")
    print(f"Text length: {len(page.text)}")
    print(f"Image size: {page.image.size}")
    
    # Save page image
    processor.save_page_image(page, f'page_{page.page_number}.png')

# Convert to multimodal documents
documents = [pdf_page_to_multimodal_document(page) for page in pages]
```

### Hybrid Search: Text + Visual

```python
from multimodal_rag import MultimodalRAGEngine

rag = MultimodalRAGEngine()

# Ingest PDFs with visual understanding
rag.ingest_pdf_directory('./research_papers')

# Queries that benefit from visual understanding:
result = rag.query("Show me the system architecture diagram")
result = rag.query("What does the data flow chart indicate?")
result = rag.query("Find pages with bar charts showing growth")
result = rag.query("Where is the formula for calculating ROI?")
```

### Integration with LLMs

```python
from multimodal_rag import MultimodalRAGEngine
import openai

# Setup RAG
rag = MultimodalRAGEngine()
rag.ingest_pdf('report.pdf', mode='multimodal')

# Query
result = rag.query("Summarize the financial results", top_k=5)

# Build context
context_parts = []
for chunk in result['retrieved_chunks']:
    page = chunk['metadata']['page_number']
    context_parts.append(f"[Page {page}]\n{chunk['text']}\n")

context = "\n---\n".join(context_parts)

# Send to LLM
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"Answer based on this PDF content:\n{context}"},
        {"role": "user", "content": result['question']}
    ]
)

print(response.choices[0].message.content)
```

## Configuration

### DPI Settings

| DPI | Quality | File Size | Speed | Use Case |
|-----|---------|-----------|-------|----------|
| 72  | Low | Small | Fast | Text-heavy documents |
| 150 | Good | Medium | Moderate | Recommended default |
| 200 | High | Large | Slow | Documents with charts |
| 300 | Very High | Very Large | Very Slow | Print quality |

```python
# Configure when initializing
rag = MultimodalRAGEngine(pdf_dpi=150)
```

### Processing Modes

| Mode | What's Embedded | Best For |
|------|----------------|----------|
| `multimodal` | Text + Image | Documents with visual content |
| `text-only` | Text only | Text-heavy documents |
| `image-only` | Image only | Scanned documents, handwriting |

## Performance Tips

### 1. Choose Appropriate DPI

```python
# Text-heavy PDFs: Lower DPI is fine
rag = MultimodalRAGEngine(pdf_dpi=100)

# PDFs with important visuals: Higher DPI
rag = MultimodalRAGEngine(pdf_dpi=200)
```

### 2. Process in Batches

```python
# Process large PDFs in page batches
total_pages = 100
batch_size = 10

for start in range(1, total_pages + 1, batch_size):
    end = min(start + batch_size - 1, total_pages)
    pages = list(range(start, end + 1))
    rag.ingest_pdf('large.pdf', pages=pages)
    rag.save()  # Save after each batch
```

### 3. Use Text-Only for Simple Documents

```python
# If your PDFs are text-only, save time
rag.ingest_pdf('text-document.pdf', mode='text-only')
```

### 4. Milvus for Large PDF Collections

```python
# For many PDFs, use Milvus
rag = MultimodalRAGEngine(vector_store_type='milvus')
rag.ingest_pdf_directory('./documents')
```

## Use Cases

### 📚 Research Papers
```python
# Process research papers with figures and tables
rag.ingest_pdf_directory('./papers', mode='multimodal')
result = rag.query("Show me papers with neural network architectures")
```

### 📊 Financial Reports
```python
# Understand charts and financial data
rag.ingest_pdf('annual_report.pdf', mode='multimodal')
result = rag.query("What does the revenue chart show?")
```

### 📖 Technical Documentation
```python
# Process manuals with diagrams
rag.ingest_pdf('user_manual.pdf', mode='multimodal')
result = rag.query("How to assemble according to the diagram?")
```

### 📝 Scanned Documents
```python
# For scanned documents, use image-only
rag.ingest_pdf('scanned.pdf', mode='image-only')
```

### 🎓 Educational Materials
```python
# Textbooks with illustrations
rag.ingest_pdf_directory('./textbooks', mode='multimodal')
result = rag.query("Explain the cell structure diagram")
```

## Troubleshooting

### PyMuPDF Not Installed

```powershell
pip install PyMuPDF Pillow
```

### Out of Memory

```python
# Use lower DPI
rag = MultimodalRAGEngine(pdf_dpi=100)

# Process fewer pages at once
rag.ingest_pdf('large.pdf', pages=[1, 2, 3])

# Use text-only mode
rag.ingest_pdf('doc.pdf', mode='text-only')
```

### Slow Processing

```python
# Lower DPI
rag = MultimodalRAGEngine(pdf_dpi=100)

# Use Milvus for better performance at scale
rag = MultimodalRAGEngine(vector_store_type='milvus', pdf_dpi=100)
```

### PDF Won't Open

```python
# Check if PDF is encrypted
from pdf_processor import PDFProcessor
processor = PDFProcessor()
info = processor.get_page_info('encrypted.pdf')  # Will show error
```

## API Reference

### MultimodalRAGEngine

```python
class MultimodalRAGEngine:
    def __init__(
        self,
        embedding_client=None,
        vector_store_type=None,
        pdf_dpi=150,
        top_k=5,
        **store_kwargs
    )
    
    def ingest_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None,
        mode: str = "multimodal"
    ) -> int
    
    def ingest_pdf_directory(
        self,
        directory: str,
        recursive: bool = True,
        mode: str = "multimodal"
    ) -> int
    
    def query(
        self,
        question: str,
        question_image: Optional[Image] = None,
        top_k: int = None
    ) -> Dict[str, Any]
```

### PDFProcessor

```python
class PDFProcessor:
    def __init__(
        self,
        dpi: int = 150,
        extract_text: bool = True,
        image_format: str = 'PNG'
    )
    
    def process_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None
    ) -> List[PDFPage]
    
    def process_pdf_directory(
        self,
        directory: str,
        recursive: bool = True
    ) -> Dict[str, List[PDFPage]]
```

## Resources

- **Qwen3-VL-Embedding**: https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
- **PyMuPDF Documentation**: https://pymupdf.readthedocs.io/
- **Pillow Documentation**: https://pillow.readthedocs.io/

## Summary

✅ **Multimodal Understanding**: Process both text and visual content from PDFs  
✅ **Easy to Use**: Simple API and launcher scripts  
✅ **Flexible**: Choose processing mode and DPI  
✅ **Scalable**: Works with FAISS or Milvus  
✅ **Production Ready**: Handle large PDF collections  

**Get started:**
```powershell
.\run.ps1 example-pdf
```

---

**Questions?** Check the [main README](README.md) or [create an issue](https://github.com/yourrepo/issues)!
