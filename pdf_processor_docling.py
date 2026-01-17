"""
PDF Processor using Docling VLM Pipeline with Granite

Clean implementation following Docling's official VLM pipeline pattern.
Uses Granite API via Docling's VLM pipeline for clean DOCTAGS output.
"""

import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import VlmPipelineOptions
    from docling.datamodel.pipeline_options_vlm_model import ApiVlmOptions, ResponseFormat
    from docling.pipeline.vlm_pipeline import VlmPipeline
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class PDFPage:
    """Represents a single PDF page with its image and metadata."""
    
    def __init__(
        self,
        page_number: int,
        image: 'Image.Image',
        text: str = "",
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a PDF page.
        
        Args:
            page_number: Page number (1-indexed)
            image: PIL Image of the page
            text: Extracted text from the page
            metadata: Additional metadata
        """
        self.page_number = page_number
        self.image = image
        self.text = text
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"PDFPage(page={self.page_number}, text_length={len(self.text)})"


def openai_compatible_vlm_options(
    model: str,
    prompt: str,
    format: ResponseFormat,
    hostname_and_port: str,
    temperature: float = 0.0,
    max_tokens: int = 4096,
    api_key: str = "",
    skip_special_tokens: bool = False,
):
    """
    Create VLM options for OpenAI-compatible APIs (Granite, LM Studio, VLLM).
    
    Args:
        model: Model name
        prompt: Prompt for the VLM
        format: Response format (DOCTAGS for clean text)
        hostname_and_port: e.g. "localhost:2222" or "100.126.235.19:2222"
        temperature: Generation temperature (0.0 for deterministic)
        max_tokens: Maximum tokens to generate
        api_key: API key if required
        skip_special_tokens: Skip special tokens (needed for VLLM)
    
    Returns:
        ApiVlmOptions configured for the endpoint
    """
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    options = ApiVlmOptions(
        url=f"http://{hostname_and_port}/v1/chat/completions",
        params=dict(
            model=model,
            max_tokens=max_tokens,
            skip_special_tokens=skip_special_tokens,
        ),
        headers=headers,
        prompt=prompt,
        timeout=120,
        scale=2.0,
        temperature=temperature,
        response_format=format,
    )
    return options


class DoclingPDFProcessor:
    """
    Process PDF files using Docling's VLM pipeline with Granite.
    
    Clean implementation following Docling's official pattern.
    Outputs clean text using DOCTAGS format (no location markers).
    """
    
    def __init__(
        self,
        api_url: str = "100.126.235.19:2222",
        model_name: str = "ibm-granite-vl",
        images_scale: float = 2.0,
        timeout: int = 120,
        prompt: str = "Convert this page to docling.",
        api_key: str = ""
    ):
        """
        Initialize Docling VLM PDF processor.
        
        Args:
            api_url: Granite API hostname:port (e.g., "100.126.235.19:2222")
            model_name: Model name for Granite VL
            images_scale: Scale factor for page images (2.0 = 144 DPI)
            timeout: API timeout in seconds
            prompt: Prompt for the VLM
            api_key: API key if required
        
        Note:
            Docling's VLM pipeline processes pages sequentially by default,
            ensuring Granite's 8192 token context window is not exceeded.
        """
        if not DOCLING_AVAILABLE:
            raise ImportError(
                "Docling is required for VLM pipeline. "
                "Install it with: pip install docling"
            )
        
        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is required for image processing. "
                "Install it with: pip install Pillow"
            )
        
        # Configure VLM pipeline following Docling's pattern
        pipeline_options = VlmPipelineOptions(
            enable_remote_services=True  # Required for remote VLM endpoints
        )
        
        # Configure Granite API using OpenAI-compatible options
        pipeline_options.vlm_options = openai_compatible_vlm_options(
            model=model_name,
            hostname_and_port=api_url,
            prompt=prompt,
            format=ResponseFormat.DOCTAGS,  # Clean structured output!
            temperature=0.0,  # Deterministic
            api_key=api_key,
        )
        
        # Create DocumentConverter with VLM pipeline
        # Note: Docling processes pages one at a time by default to avoid exceeding token limits
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options,
                    pipeline_cls=VlmPipeline,  # Use VLM pipeline!
                )
            }
        )
        
        print(f"  [INFO] Docling VLM Pipeline with Granite")
        print(f"  [INFO] API: http://{api_url}/v1/chat/completions")
        print(f"  [INFO] Model: {model_name}")
        print(f"  [INFO] Format: DOCTAGS (clean text, no location markers)")
        print(f"  [INFO] Processing: 1 page at a time (within 8192 token limit)")
    
    def process_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None,
        output_dir: Optional[str] = None
    ) -> List[PDFPage]:
        """
        Process a PDF file using Docling VLM pipeline.
        
        Args:
            pdf_path: Path to the PDF file
            pages: Optional list of page numbers to process (1-indexed)
            output_dir: Optional directory to save extracted images
        
        Returns:
            List of PDFPage objects with clean text
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Add small delay to prevent overwhelming the API (rate limiting)
        time.sleep(0.1)
        
        # Convert PDF using Docling VLM pipeline
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        # Export to clean markdown (DOCTAGS format removes location markers)
        full_markdown = doc.export_to_markdown()
        
        pdf_pages = []
        
        # Process each page
        for page_no, page in doc.pages.items():
            # Filter by requested pages if specified
            if pages is not None and page_no not in pages:
                continue
            
            # Get page image
            image = None
            try:
                if hasattr(page, 'image') and page.image and hasattr(page.image, 'pil_image'):
                    image = page.image.pil_image
                else:
                    image = page.get_image(doc)
            except Exception as e:
                print(f"  [WARNING] Could not extract image for page {page_no}: {e}")
            
            # Extract text for this specific page from the document
            page_text_parts = []
            for element, _level in doc.iterate_items():
                if hasattr(element, 'prov') and element.prov:
                    for prov in element.prov:
                        if hasattr(prov, 'page_no') and prov.page_no == page_no:
                            if hasattr(element, 'text') and element.text:
                                text_content = element.text.strip()
                                if text_content:
                                    page_text_parts.append(text_content)
                            break
            
            text = "\n\n".join(page_text_parts)
            
            # Create metadata
            metadata = {
                'source': pdf_path,
                'filename': os.path.basename(pdf_path),
                'page_number': page_no,
                'total_pages': len(doc.pages),
                'width': image.width if image else None,
                'height': image.height if image else None,
                'processor': 'docling_vlm_granite'
            }
            
            # Create PDFPage object
            pdf_page = PDFPage(
                page_number=page_no,
                image=image,
                text=text,
                metadata=metadata
            )
            
            pdf_pages.append(pdf_page)
            
            # Save image if output directory specified
            if output_dir and image:
                os.makedirs(output_dir, exist_ok=True)
                img_path = os.path.join(output_dir, f"page_{page_no}.png")
                image.save(img_path, format="PNG")
        
        return pdf_pages
    
    def process_pdf_directory(
        self,
        directory: str,
        recursive: bool = True,
        output_dir: Optional[str] = None
    ) -> Dict[str, List[PDFPage]]:
        """
        Process all PDF files in a directory.
        
        Args:
            directory: Path to directory containing PDFs
            recursive: Whether to search subdirectories
            output_dir: Optional directory to save extracted images
        
        Returns:
            Dictionary mapping PDF paths to their page lists
        """
        results = {}
        
        if recursive:
            pdf_files = list(Path(directory).rglob("*.pdf"))
        else:
            pdf_files = list(Path(directory).glob("*.pdf"))
        
        for pdf_path in pdf_files:
            try:
                # Create subdirectory for this PDF if saving images
                pdf_output_dir = None
                if output_dir:
                    pdf_name = pdf_path.stem
                    pdf_output_dir = os.path.join(output_dir, pdf_name)
                
                pages = self.process_pdf(str(pdf_path), output_dir=pdf_output_dir)
                results[str(pdf_path)] = pages
                print(f"  [OK] {pdf_path.name} ({len(pages)} pages)")
            except Exception as e:
                print(f"  [FAIL] {pdf_path.name}: {e}")
        
        return results
    
    def get_pdf_info(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get basic information about a PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary with PDF information
        """
        result = self.converter.convert(pdf_path)
        doc = result.document
        
        info = {
            'filename': os.path.basename(pdf_path),
            'path': pdf_path,
            'total_pages': len(doc.pages),
            'size_bytes': os.path.getsize(pdf_path)
        }
        
        return info


class MultimodalDocument:
    """
    Represents a document that can contain text, images, or both.
    
    This is used for multimodal RAG with vision-language models.
    """
    
    def __init__(
        self,
        text: str = "",
        image: Optional['Image.Image'] = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a multimodal document.
        
        Args:
            text: Text content
            image: PIL Image (optional)
            metadata: Document metadata
        """
        self.text = text
        self.image = image
        self.metadata = metadata or {}
    
    def has_text(self) -> bool:
        """Check if document has text."""
        return bool(self.text and self.text.strip())
    
    def has_image(self) -> bool:
        """Check if document has an image."""
        return self.image is not None
    
    def is_multimodal(self) -> bool:
        """Check if document has both text and image."""
        return self.has_text() and self.has_image()
    
    def __repr__(self):
        modalities = []
        if self.has_text():
            modalities.append(f"text({len(self.text)} chars)")
        if self.has_image():
            modalities.append(f"image({self.image.size})")
        
        return f"MultimodalDocument({', '.join(modalities)})"


def pdf_page_to_multimodal_document(pdf_page: PDFPage) -> MultimodalDocument:
    """
    Convert a PDFPage to a MultimodalDocument.
    
    Args:
        pdf_page: PDFPage object
    
    Returns:
        MultimodalDocument with both text and image
    """
    return MultimodalDocument(
        text=pdf_page.text,
        image=pdf_page.image,
        metadata=pdf_page.metadata
    )


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    print("Docling VLM Pipeline with Granite\n")
    
    if not DOCLING_AVAILABLE:
        print("Docling not installed. Install with: pip install docling")
        exit(1)
    
    print("Example usage:")
    print("""
# Initialize processor with Granite API
processor = DoclingPDFProcessor(
    api_url="100.126.235.19:2222",
    model_name="ibm-granite-vl",
    prompt="Convert this page to docling."
)

# Process a PDF
pages = processor.process_pdf('document.pdf')

# Process with output directory
pages = processor.process_pdf('document.pdf', output_dir='./output')

# Process all PDFs in a directory
results = processor.process_pdf_directory('./pdfs', output_dir='./output')

# Access clean text (no location markers!)
for page in pages:
    print(f"Page {page.page_number}:")
    print(page.text)
""")
