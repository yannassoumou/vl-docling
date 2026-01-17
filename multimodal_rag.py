#!/usr/bin/env python3
"""
Multimodal RAG Engine for PDF Processing

Leverages Qwen3-VL-Embedding's multimodal capabilities to process PDFs
with both text and visual understanding.

Based on: https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
"""

import os
from typing import List, Dict, Any, Optional
from tqdm import tqdm

from pdf_processor import PDFProcessor, PDFPage, MultimodalDocument, pdf_page_to_multimodal_document
from embedding_client import QwenEmbeddingClient
from vector_store_factory import create_vector_store
from config import TOP_K


class MultimodalChunk:
    """Represents a multimodal chunk (text + optional image)."""
    
    def __init__(
        self,
        text: str,
        image: Optional['Image.Image'] = None,
        metadata: Dict[str, Any] = None,
        chunk_id: int = None
    ):
        """
        Initialize a multimodal chunk.
        
        Args:
            text: Text content
            image: Optional PIL Image
            metadata: Chunk metadata
            chunk_id: Unique identifier
        """
        self.text = text
        self.image = image
        self.metadata = metadata or {}
        self.chunk_id = chunk_id
    
    def has_image(self) -> bool:
        """Check if chunk has an image."""
        return self.image is not None
    
    def __repr__(self):
        mode = "text+image" if self.has_image() else "text-only"
        return f"MultimodalChunk(id={self.chunk_id}, mode={mode}, text_len={len(self.text)})"


class MultimodalRAGEngine:
    """
    Multimodal RAG Engine with visual understanding.
    
    Processes PDFs page-by-page, creating embeddings that capture
    both textual and visual information using Qwen3-VL.
    """
    
    def __init__(
        self,
        embedding_client: QwenEmbeddingClient = None,
        vector_store_type: str = None,
        pdf_dpi: int = 150,
        top_k: int = TOP_K,
        **store_kwargs
    ):
        """
        Initialize the multimodal RAG engine.
        
        Args:
            embedding_client: Client for generating embeddings
            vector_store_type: Type of vector store ('faiss' or 'milvus')
            pdf_dpi: DPI for PDF rendering (higher = better quality)
            top_k: Number of documents to retrieve
            **store_kwargs: Additional arguments for vector store
        """
        self.embedding_client = embedding_client or QwenEmbeddingClient()
        self.pdf_processor = PDFProcessor(dpi=pdf_dpi)
        self.vector_store = create_vector_store(
            store_type=vector_store_type,
            embedding_client=self.embedding_client,
            **store_kwargs
        )
        self.top_k = top_k
        self.chunks = []  # Store chunks with their images
    
    def ingest_pdf(
        self,
        pdf_path: str,
        pages: Optional[List[int]] = None,
        mode: str = "multimodal"
    ) -> int:
        """
        Ingest a PDF file into the RAG system.
        
        Args:
            pdf_path: Path to PDF file
            pages: Optional list of page numbers (1-indexed)
            mode: Processing mode:
                  - 'multimodal': Use both text and images (recommended)
                  - 'text-only': Use only extracted text
                  - 'image-only': Use only page images
        
        Returns:
            Number of pages ingested
        """
        print(f"Processing PDF: {pdf_path}")
        print(f"Mode: {mode}")
        
        # Process PDF
        pdf_pages = self.pdf_processor.process_pdf(pdf_path, pages=pages)
        
        print(f"Extracted {len(pdf_pages)} pages")
        print("Generating multimodal embeddings...")
        
        # Convert to multimodal chunks
        chunks = []
        texts = []
        images = []
        
        for page in pdf_pages:
            # Create text content
            text_content = f"Page {page.page_number} from {page.metadata['filename']}"
            if page.text.strip():
                text_content += f"\n\n{page.text.strip()}"
            
            # Determine what to include based on mode
            if mode == "multimodal":
                chunk_text = text_content
                chunk_image = page.image
            elif mode == "text-only":
                chunk_text = text_content
                chunk_image = None
            elif mode == "image-only":
                chunk_text = f"Page {page.page_number} from {page.metadata['filename']}"
                chunk_image = page.image
            else:
                raise ValueError(f"Unknown mode: {mode}. Use 'multimodal', 'text-only', or 'image-only'")
            
            # Create chunk
            chunk = MultimodalChunk(
                text=chunk_text,
                image=chunk_image,
                metadata=page.metadata
            )
            
            chunks.append(chunk)
            texts.append(chunk_text)
            images.append(chunk_image)
        
        # Generate embeddings (batch processing)
        embeddings = self.embedding_client.get_embeddings(texts, images=images)
        
        # Store in vector database
        # Note: We need to adapt this for storing images too
        # For now, store text and keep images in memory
        from document_processor import DocumentChunk
        
        doc_chunks = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            doc_chunk = DocumentChunk(
                content=chunk.text,
                metadata=chunk.metadata,
                chunk_id=len(self.chunks) + i
            )
            doc_chunks.append(doc_chunk)
            
            # Store the multimodal chunk separately
            chunk.chunk_id = doc_chunk.chunk_id
            self.chunks.append(chunk)
        
        # Add to vector store (using existing infrastructure)
        # We'll store embeddings directly instead of generating them again
        self._add_chunks_with_embeddings(doc_chunks, embeddings)
        
        print(f"✓ Ingested {len(pdf_pages)} pages")
        return len(pdf_pages)
    
    def _add_chunks_with_embeddings(self, chunks: List, embeddings):
        """
        Add chunks with pre-computed embeddings to vector store.
        
        This is a helper method that bypasses re-computing embeddings.
        """
        import numpy as np
        
        # Initialize vector store if needed
        if self.vector_store.index is None:
            self.vector_store._initialize_index(embeddings.shape[1])
        
        # Assign chunk IDs
        start_id = len(self.vector_store.chunks)
        for i, chunk in enumerate(chunks):
            chunk.chunk_id = start_id + i
        
        # Add to FAISS index
        ids = np.array([chunk.chunk_id for chunk in chunks], dtype=np.int64)
        self.vector_store.index.add_with_ids(embeddings, ids)
        
        # Store chunks
        self.vector_store.chunks.extend(chunks)
    
    def ingest_pdf_directory(
        self,
        directory: str,
        recursive: bool = True,
        mode: str = "multimodal"
    ) -> int:
        """
        Ingest all PDFs from a directory.
        
        Args:
            directory: Path to directory containing PDFs
            recursive: Whether to search subdirectories (default: True)
            mode: Processing mode ('multimodal', 'text-only', 'image-only')
        
        Returns:
            Total number of pages ingested
        """
        from pathlib import Path
        
        if recursive:
            print(f"Scanning for PDFs (recursive)...")
            pdf_files = list(Path(directory).rglob("*.pdf"))
        else:
            print(f"Scanning for PDFs (non-recursive)...")
            pdf_files = list(Path(directory).glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {directory}")
            return 0
        
        print(f"Found {len(pdf_files)} PDF file(s)")
        
        total_pages = 0
        
        for i, pdf_path in enumerate(pdf_files, 1):
            rel_path = pdf_path.relative_to(directory)
            print(f"\n[{i}/{len(pdf_files)}] Processing: {rel_path}")
            
            try:
                pages = self.ingest_pdf(str(pdf_path), mode=mode)
                total_pages += pages
                print(f"  ✓ Completed: {pages} pages")
            except Exception as e:
                print(f"  ✗ Failed: {e}")
        
        print(f"\n✓ Total: {total_pages} pages from {len(pdf_files)} PDFs")
        return total_pages
    
    def query(
        self,
        question: str,
        question_image: Optional['Image.Image'] = None,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Query the multimodal RAG system.
        
        Args:
            question: Text question
            question_image: Optional image to include with the question
            top_k: Number of results to retrieve
        
        Returns:
            Dictionary with query results
        """
        k = top_k or self.top_k
        
        # Search vector store
        results = self.vector_store.search(question, top_k=k)
        
        # Retrieve chunks with their images
        retrieved = []
        for doc_chunk, score in results:
            # Find the multimodal chunk
            multimodal_chunk = None
            for chunk in self.chunks:
                if chunk.chunk_id == doc_chunk.chunk_id:
                    multimodal_chunk = chunk
                    break
            
            retrieved.append({
                'text': doc_chunk.content,
                'image': multimodal_chunk.image if multimodal_chunk else None,
                'metadata': doc_chunk.metadata,
                'score': score,
                'chunk_id': doc_chunk.chunk_id,
                'has_image': multimodal_chunk.has_image() if multimodal_chunk else False
            })
        
        return {
            'question': question,
            'retrieved_chunks': retrieved,
            'num_chunks': len(retrieved)
        }
    
    def save(self):
        """Save the RAG system state."""
        self.vector_store.save()
        # TODO: Save multimodal chunks separately
    
    def load(self):
        """Load the RAG system state."""
        return self.vector_store.load()
        # TODO: Load multimodal chunks
    
    def clear(self):
        """Clear the RAG system."""
        self.vector_store.clear()
        self.chunks = []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        stats = self.vector_store.get_stats()
        stats['multimodal_chunks'] = len(self.chunks)
        stats['chunks_with_images'] = sum(1 for c in self.chunks if c.has_image())
        return stats


if __name__ == "__main__":
    print("=" * 80)
    print("Multimodal RAG Engine - PDF Processing with Visual Understanding")
    print("=" * 80)
    print()
    
    print("Example usage:")
    print("""
from multimodal_rag import MultimodalRAGEngine

# Initialize engine
rag = MultimodalRAGEngine()

# Ingest a PDF (processes each page as text + image)
rag.ingest_pdf('document.pdf', mode='multimodal')

# Ingest entire directory
rag.ingest_pdf_directory('./pdfs', mode='multimodal')

# Query the system
result = rag.query("What is shown in the diagrams?")

# Access results with images
for chunk in result['retrieved_chunks']:
    print(f"Text: {chunk['text'][:100]}")
    print(f"Has image: {chunk['has_image']}")
    if chunk['image']:
        chunk['image'].show()  # Display the image

# Save
rag.save()
""")
