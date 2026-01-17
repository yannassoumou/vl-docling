# PDF Processing Modes - Quick Reference

## Quick Mode Selection

```yaml
# config.yaml
document_processing:
  pdf:
    processing_mode: "mode_1"  # or "mode_2"
```

## Mode 1: Docling (Fast & Simple)

**When to use**: Standard text PDFs, batch processing, local processing

**Config**:
```yaml
processing_mode: "mode_1"
mode_1:
  use_ocr: false
  images_scale: 2.0
  dpi: 150
```

**Pros**: ⚡ Fast • 💰 Free • 📴 Offline • 🔄 Batch-friendly
**Cons**: ⚠️ Limited complex layouts • ⚠️ Basic visual understanding

## Mode 2: IBM Granite VL (Advanced Vision)

**When to use**: Complex layouts, scanned docs, tables, visual elements

**Config**:
```yaml
processing_mode: "mode_2"
mode_2:
  api_url: "http://100.126.235.19:2222/v1/chat/completions"
  model_name: "ibm-granite-vl"
  timeout: 120
  dpi: 150
```

**Pros**: 🎯 Excellent accuracy • 📊 Great for tables • 👁️ Visual context
**Cons**: 🐌 Slower • 🌐 Requires API • 💰 API costs

## Usage

```python
from document_processor import DocumentProcessor

# Uses mode from config.yaml
processor = DocumentProcessor()
doc = processor.load_text_file('document.pdf')

# Check which mode was used
print(doc.metadata['processing_mode'])  # 'mode_1' or 'mode_2'
print(doc.metadata['processor'])        # 'docling' or 'granite_vl'
```

## Metadata Tracking

### Mode 1 Metadata
```python
{
    'processor': 'docling',
    'processing_mode': 'mode_1',
    'total_pages': 5
}
```

### Mode 2 Metadata
```python
{
    'processor': 'granite_vl',
    'processing_mode': 'mode_2',
    'extraction_method': 'vision_language_model',
    'total_pages': 5
}
```

## Comparison at a Glance

| Aspect | Mode 1 | Mode 2 |
|--------|--------|--------|
| Speed | ⚡⚡⚡ Fast | 🐌 Slower |
| Accuracy | ⭐⭐⭐ Good | ⭐⭐⭐⭐⭐ Excellent |
| Complex PDFs | ⭐⭐ Moderate | ⭐⭐⭐⭐⭐ Excellent |
| Setup | ✅ Simple | ⚙️ API Required |
| Cost | 💰 Free | 💰💰 API Usage |

## Troubleshooting

### Mode 1
```bash
# Install dependencies
pip install docling Pillow
```

### Mode 2
```bash
# Install dependencies
pip install PyMuPDF Pillow requests

# Test API
curl http://100.126.235.19:2222/v1/models
```

## Examples

```bash
# Run example script
python example_pdf_modes.py

# Test with your PDFs
python example_pdf.py
```

---

**💡 Tip**: Start with Mode 1, switch to Mode 2 if extraction quality is insufficient.

For detailed information, see [PDF_MODES_GUIDE.md](PDF_MODES_GUIDE.md)
