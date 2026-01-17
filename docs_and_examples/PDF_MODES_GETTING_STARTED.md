# Getting Started with PDF Processing Modes

## Quick Start (5 Minutes)

### Step 1: Choose Your Mode

Edit `config.yaml`:

```yaml
document_processing:
  pdf:
    processing_mode: "mode_1"  # or "mode_2"
```

### Step 2: Understand the Modes

**Mode 1 (Docling)**: Fast, local PDF text extraction
- ✅ Good for most PDFs
- ✅ Fast processing
- ✅ No API required

**Mode 2 (IBM Granite VL)**: Advanced vision-based extraction
- ✅ Better for complex layouts
- ✅ Excellent for tables and figures
- ⚠️ Requires API at `http://100.126.235.19:2222`

### Step 3: Process Your First PDF

```python
from document_processor import DocumentProcessor

# Initialize (uses mode from config.yaml)
processor = DocumentProcessor()

# Process a PDF
doc = processor.load_text_file('your_document.pdf')

# Check which mode was used
print(f"Processed with: {doc.metadata['processing_mode']}")
print(f"Processor: {doc.metadata['processor']}")
```

### Step 4: View Results

```python
# View extracted content
print(f"Total pages: {doc.metadata['total_pages']}")
print(f"Content length: {len(doc.content)} characters")
print(f"\nFirst 200 characters:\n{doc.content[:200]}")
```

---

## Mode Comparison

| Choose Mode 1 If... | Choose Mode 2 If... |
|--------------------|---------------------|
| Processing many simple PDFs | Need maximum accuracy |
| Want fast results | Have complex layouts |
| Working offline | Processing scanned docs |
| PDFs are text-based | PDFs have tables/figures |

---

## Configuration Examples

### Mode 1: Standard Setup
```yaml
document_processing:
  pdf:
    processing_mode: "mode_1"
    mode_1:
      use_ocr: false       # Faster, use vision model
      images_scale: 2.0    # Good quality
      dpi: 150            # Standard resolution
```

### Mode 1: High Quality (OCR)
```yaml
document_processing:
  pdf:
    processing_mode: "mode_1"
    mode_1:
      use_ocr: true       # Enable OCR for scanned PDFs
      images_scale: 3.0   # High quality
      dpi: 200           # High resolution
```

### Mode 2: Standard Setup
```yaml
document_processing:
  pdf:
    processing_mode: "mode_2"
    mode_2:
      api_url: "http://100.126.235.19:2222/v1/chat/completions"
      timeout: 120        # 2 minutes per page
      max_retries: 3      # Retry on failure
      dpi: 150           # Standard resolution
```

### Mode 2: Fast Processing
```yaml
document_processing:
  pdf:
    processing_mode: "mode_2"
    mode_2:
      api_url: "http://100.126.235.19:2222/v1/chat/completions"
      timeout: 60         # Shorter timeout
      dpi: 100           # Lower resolution (faster)
      image_format: "JPEG"  # Smaller images
      jpeg_quality: 75
```

---

## Testing Your Setup

### Test Mode 1
```bash
# Run demo script
python example_pdf_modes.py

# Or test directly
python -c "
from document_processor import DocumentProcessor
processor = DocumentProcessor()
print('Mode 1 is ready!')
"
```

### Test Mode 2
```bash
# 1. Check API is running
curl http://100.126.235.19:2222/v1/models

# 2. Set mode in config.yaml
#    processing_mode: "mode_2"

# 3. Test processing
python example_pdf_modes.py
```

---

## Common Usage Patterns

### Pattern 1: Single PDF Processing
```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
doc = processor.load_text_file('document.pdf')

print(f"Extracted {len(doc.content)} characters")
print(f"Using: {doc.metadata['processor']}")
```

### Pattern 2: Batch Processing
```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()
documents = processor.load_directory(
    'sample_pdfs',
    extensions=['.pdf'],
    recursive=True
)

for doc in documents:
    print(f"{doc.metadata['filename']}: {doc.metadata['processing_mode']}")
```

### Pattern 3: RAG Pipeline Integration
```python
from document_processor import DocumentProcessor
from embedding_client import EmbeddingClient
from vector_store_factory import VectorStoreFactory

# Process PDFs
processor = DocumentProcessor()
documents = processor.load_directory('sample_pdfs', extensions=['.pdf'])

# Chunk documents (metadata is preserved)
chunks = processor.chunk_documents(documents)

# Generate embeddings
embedding_client = EmbeddingClient()
texts = [chunk.content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]  # Includes processing_mode
embeddings = embedding_client.embed_batch(texts)

# Store in vector database
vector_store = VectorStoreFactory.create()
vector_store.add_embeddings(embeddings, texts, metadatas)

# Later: Search and see which mode extracted each result
results = vector_store.search("your query", top_k=5)
for result in results:
    print(f"Result from: {result['metadata']['processing_mode']}")
```

---

## Metadata Tracking

Every processed document includes metadata showing which mode was used:

```python
# Example metadata
{
    'source': 'path/to/document.pdf',
    'filename': 'document.pdf',
    'type': 'pdf',
    'total_pages': 5,
    'processor': 'docling',           # or 'granite_vl'
    'processing_mode': 'mode_1',      # or 'mode_2'
    'chunk_index': 0,
    'total_chunks': 10
}
```

This metadata persists through:
- ✅ Document chunking
- ✅ Embedding generation
- ✅ Vector store storage
- ✅ Search results

You can always trace back which mode extracted any piece of information!

---

## Switching Between Modes

### Quick Switch
1. Edit `config.yaml`
2. Change `processing_mode: "mode_1"` to `"mode_2"` (or vice versa)
3. Run your processing script again

### No Code Changes Required!
The mode selection is entirely configuration-driven. Your code stays the same:

```python
# This code works with BOTH modes
processor = DocumentProcessor()
doc = processor.load_text_file('document.pdf')
# Mode is determined by config.yaml
```

---

## Troubleshooting

### Mode 1 Not Working
```bash
# Install Docling
pip install docling

# Or check it's installed
python -c "import docling; print('Docling OK')"
```

### Mode 2 Not Working
```bash
# 1. Check API is accessible
curl http://100.126.235.19:2222/v1/models

# 2. Check dependencies
pip install PyMuPDF Pillow requests

# 3. Verify config.yaml has correct API URL
```

### Poor Extraction Quality (Mode 1)
```yaml
# Solution: Enable OCR
mode_1:
  use_ocr: true
  images_scale: 3.0
```

### Slow Processing (Mode 2)
```yaml
# Solution: Reduce image quality
mode_2:
  dpi: 100
  image_format: "JPEG"
  jpeg_quality: 70
```

---

## Next Steps

1. **Run the demo**: `python example_pdf_modes.py`
2. **Test with your PDFs**: Try both modes on your documents
3. **Compare results**: See which mode works better for your use case
4. **Integrate**: Use in your RAG pipeline
5. **Monitor**: Check metadata to track which mode processed each document

---

## Resources

- **Full Guide**: [PDF_MODES_GUIDE.md](PDF_MODES_GUIDE.md)
- **Quick Reference**: [PDF_MODES_QUICKREF.md](PDF_MODES_QUICKREF.md)
- **Implementation Details**: [PDF_MODES_IMPLEMENTATION_SUMMARY.md](PDF_MODES_IMPLEMENTATION_SUMMARY.md)
- **Configuration Guide**: [CONFIG_GUIDE.md](CONFIG_GUIDE.md)

---

## Support

If you encounter issues:
1. Check this guide's troubleshooting section
2. Run `python example_pdf_modes.py` to verify setup
3. Check the logs for error messages
4. Verify your configuration in `config.yaml`

---

**You're ready to go!** 🚀

Choose your mode in `config.yaml` and start processing PDFs!
