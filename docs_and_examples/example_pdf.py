#!/usr/bin/env python3
"""
Example: PDF Processing with Multimodal RAG

Demonstrates how to process PDFs with visual understanding using Qwen3-VL.
"""

from multimodal_rag import MultimodalRAGEngine
from pdf_processor import PDFProcessor
import os


def main():
    print("=" * 80)
    print("PDF Processing with Multimodal RAG")
    print("Powered by Qwen3-VL-Embedding-8B")
    print("=" * 80)
    print()
    
    # Check if sample PDFs exist
    sample_pdf_dir = "sample_pdfs"
    if not os.path.exists(sample_pdf_dir):
        print(f"Creating {sample_pdf_dir}/ directory...")
        os.makedirs(sample_pdf_dir, exist_ok=True)
        print()
        print("⚠️  No sample PDFs found.")
        print(f"   Please add PDF files to the '{sample_pdf_dir}/' directory")
        print()
        print("Example usage:")
        print_usage_examples()
        return
    
    # Initialize the multimodal RAG engine
    print("1. Initializing Multimodal RAG Engine...")
    rag = MultimodalRAGEngine(pdf_dpi=150)
    print("   ✓ Engine initialized")
    print()
    
    # List PDF files
    pdf_files = [f for f in os.listdir(sample_pdf_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("⚠️  No PDF files found in sample_pdfs/")
        print()
        print_usage_examples()
        return
    
    print(f"2. Found {len(pdf_files)} PDF file(s):")
    for pdf in pdf_files:
        print(f"   - {pdf}")
    print()
    
    # Process first PDF as example
    pdf_path = os.path.join(sample_pdf_dir, pdf_files[0])
    
    print(f"3. Processing: {pdf_files[0]}")
    print("   Mode: multimodal (text + images)")
    print()
    
    try:
        # Get PDF info first
        processor = PDFProcessor()
        info = processor.get_page_info(pdf_path)
        print(f"   PDF Information:")
        print(f"   - Total pages: {info['total_pages']}")
        print(f"   - Size: {info['size_bytes'] / 1024:.1f} KB")
        print()
        
        # Ingest PDF (multimodal: text + images)
        pages_ingested = rag.ingest_pdf(
            pdf_path,
            mode='multimodal'  # Use both text and visual information
        )
        
        print(f"   ✓ Successfully ingested {pages_ingested} pages")
        print()
        
        # Show statistics
        print("4. System Statistics:")
        stats = rag.get_stats()
        print(f"   - Total chunks: {stats.get('multimodal_chunks', 0)}")
        print(f"   - Chunks with images: {stats.get('chunks_with_images', 0)}")
        print(f"   - Embedding dimension: {stats.get('dimension', 'N/A')}")
        print()
        
        # Example queries
        print("5. Running Example Queries:")
        print()
        
        queries = [
            "What is this document about?",
            "Summarize the key points",
            "What information is shown in the figures or diagrams?"
        ]
        
        for i, question in enumerate(queries, 1):
            print(f"   Query {i}: {question}")
            
            result = rag.query(question, top_k=3)
            
            print(f"   Retrieved {result['num_chunks']} chunks:")
            for j, chunk in enumerate(result['retrieved_chunks'], 1):
                page_num = chunk['metadata'].get('page_number', '?')
                has_img = "✓" if chunk['has_image'] else "✗"
                score = chunk['score']
                
                print(f"      {j}. Page {page_num} (Score: {score:.4f}, Image: {has_img})")
                preview = chunk['text'][:80].replace('\n', ' ')
                print(f"         Preview: {preview}...")
            
            print()
        
        print("6. Multimodal Features:")
        print("   ✓ Each PDF page is processed as text + image")
        print("   ✓ Qwen3-VL understands visual content (diagrams, charts, etc.)")
        print("   ✓ Retrieval considers both textual and visual information")
        print("   ✓ Better results for documents with important visual elements")
        print()
        
    except Exception as e:
        print(f"   ✗ Error processing PDF: {e}")
        print()
        return
    
    print("=" * 80)
    print("Example completed successfully!")
    print("=" * 80)
    print()
    
    print("Next steps:")
    print("  1. Add your own PDFs to sample_pdfs/")
    print("  2. Process them with:")
    print("     python example_pdf.py")
    print("  3. Or use the launcher:")
    print("     .\\run.ps1 example-pdf")


def print_usage_examples():
    """Print usage examples."""
    print("Programmatic Usage:")
    print()
    print("```python")
    print("from multimodal_rag import MultimodalRAGEngine")
    print()
    print("# Initialize")
    print("rag = MultimodalRAGEngine()")
    print()
    print("# Process a PDF (multimodal: text + images)")
    print("rag.ingest_pdf('document.pdf', mode='multimodal')")
    print()
    print("# Or text-only mode")
    print("rag.ingest_pdf('document.pdf', mode='text-only')")
    print()
    print("# Process directory")
    print("rag.ingest_pdf_directory('./pdfs')")
    print()
    print("# Query with text")
    print("result = rag.query('What is in the document?')")
    print()
    print("# Query with image (if needed)")
    print("from PIL import Image")
    print("img = Image.open('query_image.jpg')")
    print("result = rag.query('Compare this image', question_image=img)")
    print()
    print("# Access results")
    print("for chunk in result['retrieved_chunks']:")
    print("    print(chunk['text'])")
    print("    if chunk['has_image']:")
    print("        chunk['image'].show()  # Display the page image")
    print("```")


if __name__ == "__main__":
    main()
