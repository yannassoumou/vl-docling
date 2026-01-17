"""
Example: Using Both PDF Processing Modes

This example demonstrates:
- Mode 1: Docling (simple, fast, OCR-based)
- Mode 2: IBM Granite VL (vision-based extraction via API)
"""

import os
from config_loader import load_config
from document_processor import DocumentProcessor

def print_separator():
    print("\n" + "=" * 80 + "\n")

def demonstrate_mode_1():
    """Demonstrate Mode 1: Docling PDF processing."""
    print("MODE 1: DOCLING PDF PROCESSING")
    print("-" * 80)
    print("Description: Fast, OCR-based PDF text extraction")
    print("Uses: Docling library for document understanding")
    print("-" * 80)
    
    # Check if Mode 1 is available
    try:
        from pdf_processor_docling import DoclingPDFProcessor
        mode1_available = True
        print("\n[OK] Mode 1 processor is available")
    except ImportError:
        mode1_available = False
        print("\n[NOT AVAILABLE] Mode 1 processor not available")
        print("    Install with: pip install docling")
    
    # Load config to show Mode 1 settings
    config = load_config()
    pdf_config = config.get('document_processing', {}).get('pdf', {})
    mode1_config = pdf_config.get('mode_1', {})
    
    print(f"\n[INFO] Mode 1 Configuration:")
    print(f"  DPI: {mode1_config.get('dpi', 'Not configured')}")
    print(f"  Use OCR: {mode1_config.get('use_ocr', 'Not configured')}")
    print(f"  Images Scale: {mode1_config.get('images_scale', 'Not configured')}")
    print(f"  Extract Text: {mode1_config.get('extract_text', 'Not configured')}")
    
    print("\n[INFO] To use Mode 1, set in config.yaml:")
    print("      document_processing:")
    print("        pdf:")
    print("          processing_mode: 'mode_1'")

def demonstrate_mode_2():
    """Demonstrate Mode 2: IBM Granite VL processing."""
    print("MODE 2: IBM GRANITE VL PROCESSING")
    print("-" * 80)
    print("Description: Vision-based PDF text extraction")
    print("Uses: IBM Granite VL model via API (port 2222)")
    print("Benefits: Better understanding of complex layouts and visual elements")
    print("-" * 80)
    
    # Load config to check Mode 2 settings
    config = load_config()
    pdf_config = config.get('document_processing', {}).get('pdf', {})
    mode2_config = pdf_config.get('mode_2', {})
    
    print(f"\n[INFO] Mode 2 Configuration:")
    print(f"  API URL: {mode2_config.get('api_url', 'Not configured')}")
    print(f"  Model: {mode2_config.get('model_name', 'Not configured')}")
    print(f"  Timeout: {mode2_config.get('timeout', 'Not configured')}s")
    print(f"  Max Retries: {mode2_config.get('max_retries', 'Not configured')}")
    
    print("\n[INFO] To use Mode 2, set in config.yaml:")
    print("      document_processing:")
    print("        pdf:")
    print("          processing_mode: 'mode_2'")
    
    # Example: Process with Mode 2
    # Note: Requires IBM Granite VL API to be running on port 2222
    # processor = DocumentProcessor()
    # pdf_path = "sample_pdfs/example.pdf"
    # if os.path.exists(pdf_path):
    #     doc = processor.load_text_file(pdf_path)
    #     print(f"\n[OK] Processed: {doc.metadata['filename']}")
    #     print(f"  Total pages: {doc.metadata.get('total_pages', 'N/A')}")
    #     print(f"  Processor: {doc.metadata.get('processor', 'N/A')}")
    #     print(f"  Processing mode: {doc.metadata.get('processing_mode', 'N/A')}")
    #     print(f"  Extraction method: {doc.metadata.get('extraction_method', 'N/A')}")

def show_metadata_tracking():
    """Show how metadata tracks the processing mode."""
    print("METADATA TRACKING")
    print("-" * 80)
    print("Each processed document includes metadata to track the processing mode:")
    print()
    print("Mode 1 (Docling) metadata:")
    print("  {")
    print("    'source': 'path/to/document.pdf',")
    print("    'filename': 'document.pdf',")
    print("    'type': 'pdf',")
    print("    'total_pages': 5,")
    print("    'processor': 'docling',")
    print("    'processing_mode': 'mode_1'")
    print("  }")
    print()
    print("Mode 2 (IBM Granite VL) metadata:")
    print("  {")
    print("    'source': 'path/to/document.pdf',")
    print("    'filename': 'document.pdf',")
    print("    'type': 'pdf',")
    print("    'total_pages': 5,")
    print("    'processor': 'granite_vl',")
    print("    'processing_mode': 'mode_2',")
    print("    'extraction_method': 'vision_language_model'")
    print("  }")

def compare_modes():
    """Compare the two processing modes."""
    print("MODE COMPARISON")
    print("-" * 80)
    print()
    print("+----------------+---------------------+---------------------+")
    print("| Feature        | Mode 1 (Docling)    | Mode 2 (Granite VL) |")
    print("+----------------+---------------------+---------------------+")
    print("| Speed          | Fast                | Slower (API calls)  |")
    print("| Accuracy       | Good for text PDFs  | Better for complex  |")
    print("| Complex Layout | Moderate            | Excellent           |")
    print("| Visual Element | Limited             | Excellent           |")
    print("| Tables         | Good                | Excellent           |")
    print("| Handwriting    | Requires OCR        | Better understand   |")
    print("| Setup          | Simple (library)    | Requires API server |")
    print("| Dependencies   | docling, Pillow     | PyMuPDF, Pillow     |")
    print("| Cost           | Free (local)        | API compute time    |")
    print("+----------------+---------------------+---------------------+")
    print()
    print("Recommendation:")
    print("  - Use Mode 1 for: Simple text PDFs, batch processing, local processing")
    print("  - Use Mode 2 for: Complex layouts, tables, visual elements, scanned docs")

def main():
    """Main example function."""
    print_separator()
    print("PDF PROCESSING MODES DEMONSTRATION")
    print_separator()
    
    # Load and display current configuration
    config = load_config()
    pdf_config = config.get('document_processing', {}).get('pdf', {})
    current_mode = pdf_config.get('processing_mode', 'mode_1')
    
    print(f"Current Mode: {current_mode.upper()}")
    print_separator()
    
    # Demonstrate Mode 1
    demonstrate_mode_1()
    print_separator()
    
    # Demonstrate Mode 2
    demonstrate_mode_2()
    print_separator()
    
    # Show metadata tracking
    show_metadata_tracking()
    print_separator()
    
    # Compare modes
    compare_modes()
    print_separator()
    
    print("QUICK START")
    print("-" * 80)
    print()
    print("1. Choose your mode in config.yaml:")
    print("   processing_mode: 'mode_1'  # or 'mode_2'")
    print()
    print("2. For Mode 2, ensure IBM Granite VL API is running:")
    print("   - Endpoint: http://100.126.235.19:2222/v1/chat/completions")
    print("   - Check config.yaml mode_2 section for API settings")
    print()
    print("3. Process PDFs:")
    print("   from document_processor import DocumentProcessor")
    print("   processor = DocumentProcessor()")
    print("   doc = processor.load_text_file('document.pdf')")
    print("   print(doc.metadata['processing_mode'])  # Shows which mode was used")
    print()
    print("4. The metadata will track which processor extracted the information:")
    print("   - 'processor': 'docling' or 'granite_vl'")
    print("   - 'processing_mode': 'mode_1' or 'mode_2'")
    print_separator()

if __name__ == "__main__":
    main()
