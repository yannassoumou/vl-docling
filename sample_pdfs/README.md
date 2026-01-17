# Sample PDFs Directory

Place your PDF files here to test multimodal RAG with visual understanding!

## Quick Start

1. **Add your PDFs** to this directory
2. **Run the example**:
   ```powershell
   # Windows PowerShell
   .\run.ps1 example-pdf
   
   # Linux/Mac
   ./run.sh example-pdf
   ```

## What Happens

Each PDF page is processed as:
- **Text**: Extracted text content
- **Image**: Visual rendering at 150 DPI

Both are embedded together using **Qwen3-VL-Embedding-8B** for true multimodal understanding!

## Supported PDF Types

✅ Research papers with figures and charts  
✅ Financial reports with data visualizations  
✅ Technical documentation with diagrams  
✅ Presentations saved as PDF  
✅ Scanned documents  
✅ Forms and worksheets  

## Example Usage

```python
from multimodal_rag import MultimodalRAGEngine

# Initialize
rag = MultimodalRAGEngine()

# Process all PDFs in this directory
rag.ingest_pdf_directory('./sample_pdfs')

# Query with visual understanding
result = rag.query("What information is shown in the charts?")
```

## Need Sample PDFs?

You can use any PDF files! Here are some suggestions:

- Academic papers from arXiv
- Company annual reports
- Technical documentation
- Your own documents

## Learn More

See [PDF_GUIDE.md](../PDF_GUIDE.md) for complete documentation.
