import os
from typing import List, Dict, Any
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
from config import CHUNK_SIZE, CHUNK_OVERLAP
from config_loader import load_config

# Import Docling VLM processor with Granite integration
try:
    from pdf_processor_docling import DoclingPDFProcessor, pdf_page_to_multimodal_document
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("[WARNING] Docling with Granite VLM not available. PDF processing disabled.")


# Global function for parallel processing (must be at module level for pickling)
def _process_single_file(args):
    """
    Process a single file. Used by ProcessPoolExecutor.
    
    Args:
        args: tuple of (file_path, directory_path, is_pdf, pdf_mode_override)
    
    Returns:
        tuple of (document, relative_path, error)
    """
    file_path, directory_path, is_pdf = args
    rel_file = os.path.relpath(file_path, directory_path)
    
    try:
        if is_pdf:
            # Use Docling VLM pipeline with Granite API
            if not PDF_SUPPORT:
                raise ImportError("Docling with Granite VLM is required for PDF processing. Install with: pip install docling")
            
            config = load_config()
            pdf_config = config.get('document_processing', {}).get('pdf', {}).get('mode_2', {})
            
            # Extract hostname:port from api_url
            api_url_full = pdf_config.get('api_url', 'http://100.126.235.19:2222/v1/chat/completions')
            import re
            match = re.search(r'https?://([^/]+)', api_url_full)
            hostname_port = match.group(1) if match else "100.126.235.19:2222"
            
            # Initialize Docling VLM processor with Granite
            pdf_processor = DoclingPDFProcessor(
                api_url=hostname_port,
                model_name=pdf_config.get('model_name', 'ibm-granite-vl'),
                images_scale=pdf_config.get('images_scale', 2.0),
                timeout=pdf_config.get('timeout', 120),
                prompt=pdf_config.get('user_prompt', 'Convert this page to docling.')
            )
            
            # Process PDF
            pages = pdf_processor.process_pdf(file_path)
            
            # Combine text from all pages
            all_text = []
            for page in pages:
                page_header = f"\n\n=== Page {page.page_number} ===\n\n"
                all_text.append(page_header + page.text)
            
            content = "".join(all_text)
            
            metadata = {
                'source': file_path,
                'filename': os.path.basename(file_path),
                'type': 'pdf',
                'total_pages': len(pages),
                'processor': 'granite_vlm'
            }
            
            doc = Document(content=content, metadata=metadata)
        else:
            # Regular text file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = {
                'source': file_path,
                'filename': os.path.basename(file_path)
            }
            
            doc = Document(content=content, metadata=metadata)
        
        return (doc, rel_file, None)
    except Exception as e:
        return (None, rel_file, str(e))


class Document:
    """Represents a document with content and metadata."""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None):
        """
        Initialize a document.
        
        Args:
            content: The text content of the document
            metadata: Optional metadata dictionary
        """
        self.content = content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"Document(content_length={len(self.content)}, metadata={self.metadata})"


class DocumentChunk:
    """Represents a chunk of a document."""
    
    def __init__(self, content: str, metadata: Dict[str, Any] = None, chunk_id: int = None):
        """
        Initialize a document chunk.
        
        Args:
            content: The text content of the chunk
            metadata: Optional metadata dictionary
            chunk_id: Unique identifier for the chunk
        """
        self.content = content
        self.metadata = metadata or {}
        self.chunk_id = chunk_id
    
    def __repr__(self):
        return f"DocumentChunk(id={self.chunk_id}, content_length={len(self.content)})"


class DocumentProcessor:
    """Processes documents and splits them into chunks."""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize the document processor.
        Uses Granite VLM for all PDF processing.
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between consecutive chunks in characters
        """
        self.chunk_size = chunk_size or CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or CHUNK_OVERLAP
        
        # Initialize PDF processor (Granite VLM only)
        self.pdf_processor = None
        self.processor_name = 'granite_vlm'
        
        if PDF_SUPPORT:
            # Load configuration for Granite VLM
            config = load_config()
            pdf_config = config.get('document_processing', {}).get('pdf', {}).get('mode_2', {})
            
            # Extract hostname:port from api_url
            api_url_full = pdf_config.get('api_url', 'http://100.126.235.19:2222/v1/chat/completions')
            import re
            match = re.search(r'https?://([^/]+)', api_url_full)
            hostname_port = match.group(1) if match else "100.126.235.19:2222"
            
            # Initialize Docling VLM processor with Granite
            self.pdf_processor = DoclingPDFProcessor(
                api_url=hostname_port,
                model_name=pdf_config.get('model_name', 'ibm-granite-vl'),
                images_scale=pdf_config.get('images_scale', 2.0),
                timeout=pdf_config.get('timeout', 120),
                prompt=pdf_config.get('user_prompt', 'Convert this page to docling.')
            )
        else:
            print("  [WARNING] Docling with Granite VLM not available")
            print("  [INFO] Install dependencies: pip install docling")
    
    def load_text_file(self, file_path: str) -> Document:
        """
        Load a text file as a document.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Document object
        """
        # Handle PDF files separately
        if file_path.lower().endswith('.pdf'):
            return self._load_pdf_file(file_path)
        
        # Regular text file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = {
            'source': file_path,
            'filename': os.path.basename(file_path)
        }
        
        return Document(content=content, metadata=metadata)
    
    def _load_pdf_file(self, file_path: str) -> Document:
        """
        Load a PDF file as a document using Docling or PyMuPDF.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Document object with extracted text from all pages
        """
        if not PDF_SUPPORT or not self.pdf_processor:
            raise ImportError(
                "PDF support not available. Install docling: pip install docling"
            )
        
        try:
            # Process PDF pages
            pages = self.pdf_processor.process_pdf(file_path)
            
            # Combine text from all pages
            all_text = []
            for page in pages:
                page_header = f"\n\n=== Page {page.page_number} ===\n\n"
                all_text.append(page_header + page.text)
            
            content = "".join(all_text)
            
            metadata = {
                'source': file_path,
                'filename': os.path.basename(file_path),
                'type': 'pdf',
                'total_pages': len(pages),
                'processor': self.processor_name
            }
            
            return Document(content=content, metadata=metadata)
            
        except Exception as e:
            # If PDF processing fails, raise with descriptive error
            raise Exception(f"Failed to process PDF {file_path}: {str(e)}")
    
    def _load_file_safe(self, file_path: str, directory_path: str) -> tuple:
        """
        Safely load a file and return result with status.
        Helper method for parallel processing.
        """
        rel_file = os.path.relpath(file_path, directory_path)
        try:
            doc = self.load_text_file(file_path)
            return (doc, rel_file, None)  # (document, path, error)
        except Exception as e:
            return (None, rel_file, str(e))
    
    def load_directory(self, directory_path: str, extensions: List[str] = None, recursive: bool = True, parallel: bool = None, max_workers: int = None) -> List[Document]:
        """
        Load all text files from a directory.
        
        Args:
            directory_path: Path to the directory
            extensions: List of file extensions to include (e.g., ['.txt', '.md'])
            recursive: If True, search subdirectories recursively (default: True)
            parallel: If True, process files in parallel (None = use config setting)
            max_workers: Number of parallel workers (None = use config setting or CPU count)
            
        Returns:
            List of Document objects
        """
        if extensions is None:
            extensions = ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.pdf']
        
        # Load config for parallel settings
        config = load_config()
        parallel_config = config.get('document_processing', {}).get('parallel', {})
        
        if parallel is None:
            parallel = parallel_config.get('enabled', True)
        
        if max_workers is None:
            max_workers = parallel_config.get('max_workers') or cpu_count()
        
        min_files_for_parallel = parallel_config.get('min_files_for_parallel', 2)
        parallel_mode = parallel_config.get('mode', 'process')  # 'process' or 'thread'
        
        documents = []
        
        # Collect all files first
        all_files = []
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
        else:
            try:
                files = os.listdir(directory_path)
                for file in files:
                    file_path = os.path.join(directory_path, file)
                    if os.path.isfile(file_path) and any(file.endswith(ext) for ext in extensions):
                        all_files.append(file_path)
            except Exception as e:
                print(f"Error accessing directory: {str(e)}")
                return documents
        
        if not all_files:
            return documents
        
        print(f"  Found {len(all_files)} files to process...")
        if parallel and len(all_files) >= min_files_for_parallel:
            if parallel_mode == 'process':
                print(f"  Using {max_workers} parallel workers (multiprocessing - TRUE PARALLEL)")
                
                # Prepare arguments for parallel processing
                process_args = [
                    (file_path, directory_path, file_path.lower().endswith('.pdf'))
                    for file_path in all_files
                ]
                
                # Use ProcessPoolExecutor for true parallel processing (bypasses GIL)
                try:
                    with ProcessPoolExecutor(max_workers=max_workers) as executor:
                        # Submit all tasks
                        futures = [executor.submit(_process_single_file, args) for args in process_args]
                        
                        # Collect results as they complete
                        completed = 0
                        for future in as_completed(futures):
                            doc, rel_file, error = future.result()
                            completed += 1
                            
                            if doc:
                                documents.append(doc)
                                print(f"    [{completed}/{len(all_files)}] [OK] {rel_file}")
                            else:
                                print(f"    [{completed}/{len(all_files)}] [FAIL] {rel_file}: {error}")
                except Exception as e:
                    print(f"  [WARNING] Multiprocessing failed: {e}")
                    print(f"  [INFO] Falling back to sequential processing...")
                    parallel = False
            else:
                # Thread-based parallelism (limited by GIL but more compatible)
                print(f"  Using {max_workers} parallel workers (threading - limited by GIL)")
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_file = {
                        executor.submit(self._load_file_safe, file_path, directory_path): file_path 
                        for file_path in all_files
                    }
                    
                    completed = 0
                    for future in as_completed(future_to_file):
                        doc, rel_file, error = future.result()
                        completed += 1
                        
                        if doc:
                            documents.append(doc)
                            print(f"    [{completed}/{len(all_files)}] [OK] {rel_file}")
                        else:
                            print(f"    [{completed}/{len(all_files)}] [FAIL] {rel_file}: {error}")
        
        if not parallel or len(all_files) < min_files_for_parallel:
            # Sequential processing (for small file counts or when parallel is disabled)
            print(f"  Using sequential processing")
            for i, file_path in enumerate(all_files, 1):
                rel_file = os.path.relpath(file_path, directory_path)
                try:
                    doc = self.load_text_file(file_path)
                    documents.append(doc)
                    print(f"    [{i}/{len(all_files)}] [OK] {rel_file}")
                except Exception as e:
                    print(f"    [{i}/{len(all_files)}] [FAIL] {rel_file}: {str(e)}")
        
        return documents
    
    def split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]
            
            # If not the last chunk, try to break at a sentence or word boundary
            if end < len(text):
                # Try to find the last period, question mark, or exclamation point
                last_sentence = max(
                    chunk.rfind('. '),
                    chunk.rfind('? '),
                    chunk.rfind('! ')
                )
                
                if last_sentence > self.chunk_size // 2:
                    chunk = chunk[:last_sentence + 1]
                    end = start + last_sentence + 1
                # Otherwise, try to find the last space
                elif ' ' in chunk:
                    last_space = chunk.rfind(' ')
                    if last_space > self.chunk_size // 2:
                        chunk = chunk[:last_space]
                        end = start + last_space
            
            chunks.append(chunk.strip())
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Avoid infinite loop
            if start <= end - self.chunk_size:
                start = end
        
        return [c for c in chunks if c]  # Remove empty chunks
    
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """
        Split a document into chunks.
        
        Args:
            document: Document to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        text_chunks = self.split_text(document.content)
        
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            metadata = document.metadata.copy()
            metadata['chunk_index'] = i
            metadata['total_chunks'] = len(text_chunks)
            
            chunk = DocumentChunk(
                content=chunk_text,
                metadata=metadata,
                chunk_id=None  # Will be assigned by vector store
            )
            chunks.append(chunk)
        
        return chunks
    
    def chunk_documents(self, documents: List[Document]) -> List[DocumentChunk]:
        """
        Split multiple documents into chunks.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of DocumentChunk objects
        """
        all_chunks = []
        for doc in documents:
            chunks = self.chunk_document(doc)
            all_chunks.extend(chunks)
        
        return all_chunks


if __name__ == "__main__":
    # Test the document processor
    processor = DocumentProcessor(chunk_size=200, chunk_overlap=20)
    
    # Test text splitting
    sample_text = """
    Artificial intelligence is the simulation of human intelligence by machines.
    Machine learning is a subset of AI that enables systems to learn from data.
    Deep learning uses neural networks with multiple layers.
    Natural language processing helps computers understand human language.
    """
    
    chunks = processor.split_text(sample_text)
    print(f"Created {len(chunks)} chunks from sample text")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}: {chunk[:50]}...")
