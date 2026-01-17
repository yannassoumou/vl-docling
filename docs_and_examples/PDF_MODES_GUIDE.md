# PDF Processing Modes Guide

This guide explains the two PDF processing modes available in the RAG system and how to choose between them.

## Overview

The system now supports **two distinct PDF processing modes**:

- **Mode 1**: Docling-based processing (fast, OCR-based)
- **Mode 2**: IBM Granite VL model (vision-based extraction via API)

Each mode has different strengths and is optimized for different use cases.

---

## Mode 1: Docling Processing

### Description
Mode 1 uses the Docling library for fast, efficient PDF text extraction. It's optimized for standard text-based PDFs with simple to moderate layouts.

### Key Features
- ✅ Fast processing speed
- ✅ Good for text-heavy PDFs
- ✅ Local processing (no API calls)
- ✅ Low latency
- ✅ Free (no API costs)
- ✅ Table extraction support
- ⚠️ Moderate handling of complex layouts
- ⚠️ Limited understanding of visual context

### Best For
- Simple text PDFs
- Batch processing of many documents
- When speed is critical
- Local/offline processing
- Standard document formats

### Configuration

In `config.yaml`:

```yaml
document_processing:
  pdf:
    processing_mode: "mode_1"
    
    mode_1:
      dpi: 150                  # Page rendering quality
      use_ocr: false            # Enable OCR for scanned PDFs
      images_scale: 2.0         # Image scale factor (2.0 = ~144 DPI)
      extract_text: true        # Extract text from PDFs
```

### Metadata Output

Documents processed with Mode 1 include this metadata:

```python
{
    'source': 'path/to/document.pdf',
    'filename': 'document.pdf',
    'type': 'pdf',
    'total_pages': 5,
    'processor': 'docling',
    'processing_mode': 'mode_1',
    'width': 1024,
    'height': 768
}
```

---

## Mode 2: IBM Granite VL Processing

### Description
Mode 2 leverages IBM's Granite Vision-Language model to extract text from PDFs using advanced visual understanding. The model "sees" each page as an image and extracts text with better understanding of layout and visual context.

### Key Features
- ✅ Excellent handling of complex layouts
- ✅ Superior understanding of visual elements
- ✅ Better table extraction
- ✅ Works well with scanned documents
- ✅ Can handle handwriting (with appropriate model)
- ✅ Understands visual context
- ⚠️ Slower (API latency)
- ⚠️ Requires running API server
- ⚠️ API compute costs

### Best For
- Complex PDF layouts
- Documents with tables and figures
- Scanned documents
- PDFs with visual elements
- When accuracy is more important than speed
- Forms and structured documents

### Configuration

In `config.yaml`:

```yaml
document_processing:
  pdf:
    processing_mode: "mode_2"
    
    mode_2:
      # IBM Granite VL API endpoint
      api_url: "http://100.126.235.19:2222/v1/chat/completions"
      model_name: "ibm-granite-vl"
      timeout: 120              # API timeout (seconds)
      max_retries: 3            # Number of retries on failure
      dpi: 150                  # Page rendering quality
      image_format: "PNG"       # Image format to send to API
      jpeg_quality: 85          # JPEG quality (if using JPEG)
      
      # Prompts for the VL model
      system_prompt: "You are an expert document analyzer. Extract all text content from the provided PDF page image, preserving structure and formatting."
      user_prompt: "Extract all text from this PDF page. Preserve headings, paragraphs, lists, and tables. Provide the extracted text only."
```

### Prerequisites

1. **IBM Granite VL API Server**: Must be running and accessible
   - Default endpoint: `http://100.126.235.19:2222/v1/chat/completions`
   - Ensure the server is online before processing

2. **Dependencies**: 
   ```bash
   pip install PyMuPDF Pillow requests
   ```

### Metadata Output

Documents processed with Mode 2 include this metadata:

```python
{
    'source': 'path/to/document.pdf',
    'filename': 'document.pdf',
    'type': 'pdf',
    'total_pages': 5,
    'processor': 'granite_vl',
    'processing_mode': 'mode_2',
    'extraction_method': 'vision_language_model',
    'width': 1024,
    'height': 768,
    'dpi': 150
}
```

---

## Switching Between Modes

### Method 1: Configuration File

Edit `config.yaml`:

```yaml
document_processing:
  pdf:
    processing_mode: "mode_1"  # Change to "mode_2" for IBM Granite VL
```

Then restart your application or reload the configuration.

### Method 2: Programmatic Selection

While the configuration sets the default mode, you can verify which mode is being used:

```python
from config_loader import load_config
from document_processor import DocumentProcessor

# Load configuration
config = load_config()
pdf_config = config.get('document_processing', {}).get('pdf', {})
current_mode = pdf_config.get('processing_mode', 'mode_1')

print(f"Current PDF processing mode: {current_mode}")

# Process a PDF
processor = DocumentProcessor()
doc = processor.load_text_file('document.pdf')

# Check which mode was used
print(f"Processed with: {doc.metadata['processor']}")
print(f"Processing mode: {doc.metadata['processing_mode']}")
```

---

## Mode Comparison Table

| Feature | Mode 1 (Docling) | Mode 2 (Granite VL) |
|---------|------------------|---------------------|
| **Speed** | Fast | Slower (API calls) |
| **Accuracy** | Good for text PDFs | Better for complex layouts |
| **Complex Layouts** | Moderate | Excellent |
| **Visual Elements** | Limited | Excellent |
| **Tables** | Good | Excellent |
| **Scanned Documents** | Requires OCR | Better understanding |
| **Handwriting** | Limited (OCR-dependent) | Better (model-dependent) |
| **Setup** | Simple (library install) | Requires API server |
| **Dependencies** | docling, Pillow | PyMuPDF, Pillow, requests |
| **Cost** | Free (local) | API compute time |
| **Latency** | Low | Higher (API calls) |
| **Offline Use** | Yes | No (requires API) |

---

## Usage Examples

### Example 1: Process Single PDF

```python
from document_processor import DocumentProcessor

# Initialize processor (uses mode from config.yaml)
processor = DocumentProcessor()

# Process a PDF
doc = processor.load_text_file('document.pdf')

# Access extracted content
print(f"Content length: {len(doc.content)} characters")
print(f"Total pages: {doc.metadata['total_pages']}")
print(f"Processed with: {doc.metadata['processor']}")
print(f"Mode: {doc.metadata['processing_mode']}")
```

### Example 2: Process Directory of PDFs

```python
from document_processor import DocumentProcessor

processor = DocumentProcessor()

# Process all PDFs in a directory
documents = processor.load_directory(
    'sample_pdfs',
    extensions=['.pdf'],
    recursive=True
)

# Check results
for doc in documents:
    print(f"\n{doc.metadata['filename']}:")
    print(f"  Mode: {doc.metadata.get('processing_mode', 'N/A')}")
    print(f"  Processor: {doc.metadata.get('processor', 'N/A')}")
    print(f"  Pages: {doc.metadata.get('total_pages', 'N/A')}")
```

### Example 3: RAG Pipeline with Metadata Tracking

```python
from document_processor import DocumentProcessor
from embedding_client import EmbeddingClient
from vector_store_factory import VectorStoreFactory

# Initialize components
processor = DocumentProcessor()
embedding_client = EmbeddingClient()
vector_store = VectorStoreFactory.create()

# Process PDFs
documents = processor.load_directory('sample_pdfs', extensions=['.pdf'])

# Chunk documents
chunks = processor.chunk_documents(documents)

# The metadata persists through chunking
for chunk in chunks:
    print(f"Chunk from: {chunk.metadata.get('filename')}")
    print(f"  Processing mode: {chunk.metadata.get('processing_mode')}")
    print(f"  Processor: {chunk.metadata.get('processor')}")

# Generate embeddings and store
# The metadata (including processing_mode) is stored with each chunk
texts = [chunk.content for chunk in chunks]
metadatas = [chunk.metadata for chunk in chunks]

embeddings = embedding_client.embed_batch(texts)
vector_store.add_embeddings(embeddings, texts, metadatas)

# Later, when retrieving, you can see which mode was used
results = vector_store.search("query", top_k=5)
for result in results:
    print(f"Result from: {result['metadata'].get('processing_mode')}")
```

---

## Troubleshooting

### Mode 1 Issues

**Problem**: "Docling not available"
```bash
# Solution: Install docling
pip install docling
```

**Problem**: Poor text extraction quality
```yaml
# Solution: Enable OCR in config.yaml
document_processing:
  pdf:
    mode_1:
      use_ocr: true
      images_scale: 3.0  # Higher quality
```

### Mode 2 Issues

**Problem**: "Connection refused" or timeout errors
```bash
# Solution: Verify IBM Granite VL API is running
# Check the endpoint is accessible:
curl http://100.126.235.19:2222/v1/models
```

**Problem**: Slow processing
```yaml
# Solution: Reduce image quality or increase timeout
document_processing:
  pdf:
    mode_2:
      dpi: 100          # Lower DPI = smaller images = faster
      timeout: 180      # Increase timeout
      image_format: "JPEG"  # JPEG is smaller than PNG
      jpeg_quality: 75  # Lower quality = smaller images
```

**Problem**: API errors
```yaml
# Solution: Increase retry count
document_processing:
  pdf:
    mode_2:
      max_retries: 5
```

---

## Performance Considerations

### Mode 1 Performance

- **Processing time**: ~1-2 seconds per page (local)
- **Memory usage**: Moderate
- **Batch processing**: Excellent (can process 100+ PDFs efficiently)
- **Parallelization**: Fully supported

### Mode 2 Performance

- **Processing time**: ~5-15 seconds per page (depends on API latency)
- **Memory usage**: Low (processing happens on API server)
- **Batch processing**: Good (but limited by API capacity)
- **Parallelization**: Limited by API server capacity

### Optimization Tips

**For Mode 1**:
- Disable OCR if not needed (`use_ocr: false`)
- Use moderate DPI (150 is usually sufficient)
- Enable parallel processing for multiple files

**For Mode 2**:
- Use JPEG format for faster transfers
- Reduce DPI if quality is acceptable
- Consider rate limiting for batch processing
- Monitor API server capacity

---

## Best Practices

1. **Start with Mode 1** for most use cases
2. **Switch to Mode 2** if you encounter:
   - Poor extraction quality
   - Complex layouts
   - Heavy use of tables/figures
   - Scanned documents

3. **Monitor metadata** to track which mode was used for each document

4. **Test both modes** on sample documents to determine which works best for your use case

5. **Consider hybrid approach**: Use Mode 1 for bulk processing, Mode 2 for complex documents

---

## Future Enhancements

Potential future improvements:

- [ ] Automatic mode selection based on document complexity
- [ ] Hybrid processing (combine both modes)
- [ ] Mode 3: Additional processors (e.g., AWS Textract, Google Vision)
- [ ] Per-document mode selection
- [ ] Quality metrics and comparison tools

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your configuration in `config.yaml`
3. Check the example script: `python example_pdf_modes.py`
4. Review logs for error messages

---

**Related Documentation**:
- [PDF Processing Guide](PDF_GUIDE.md)
- [Configuration Guide](CONFIG_GUIDE.md)
- [Quick Start Guide](QUICKSTART.md)
