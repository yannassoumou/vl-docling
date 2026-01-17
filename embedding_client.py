import requests
import numpy as np
import base64
import io
from typing import List, Union, Optional, Dict, Any
from config import EMBEDDING_API_URL

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class QwenEmbeddingClient:
    """
    Client for interacting with Qwen3VL embedding API.
    
    Supports multimodal embeddings (text, images, or text+image combinations).
    Based on: https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B
    """
    
    def __init__(self, api_url: str = None):
        """
        Initialize the embedding client.
        
        Args:
            api_url: URL of the embedding API endpoint
        """
        self.api_url = api_url or EMBEDDING_API_URL
        self.headers = {"Content-Type": "application/json"}
    
    def _image_to_base64(self, image: 'Image.Image') -> str:
        """
        Convert PIL Image to base64 string.
        
        Args:
            image: PIL Image object
        
        Returns:
            Base64 encoded string
        """
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def get_embeddings(
        self,
        texts: Union[str, List[str]],
        images: Optional[Union['Image.Image', List[Optional['Image.Image']]]] = None
    ) -> np.ndarray:
        """
        Get embeddings for text, images, or text+image combinations.
        
        Qwen3-VL-Embedding supports:
        - Text only
        - Image only
        - Text + Image (multimodal)
        
        Args:
            texts: Single text string or list of text strings
            images: Optional PIL Image or list of PIL Images (can be None for text-only)
            
        Returns:
            numpy array of embeddings with shape (n_inputs, embedding_dim)
        
        Examples:
            # Text only
            embeddings = client.get_embeddings("Hello world")
            
            # Text + Image
            embeddings = client.get_embeddings("A cat", images=cat_image)
            
            # Batch with mixed modalities
            embeddings = client.get_embeddings(
                ["Text 1", "Text 2"],
                images=[image1, None]  # Second input is text-only
            )
        """
        # Convert single string to list
        if isinstance(texts, str):
            texts = [texts]
        
        # Handle images
        if images is None:
            # No images, text-only mode
            return self._get_text_embeddings(texts)
        
        # Convert single image to list
        if not isinstance(images, list):
            images = [images]
        
        # Ensure images list matches texts length
        if len(images) != len(texts):
            if len(images) == 1:
                # Broadcast single image to all texts
                images = images * len(texts)
            else:
                raise ValueError(
                    f"Number of images ({len(images)}) must match "
                    f"number of texts ({len(texts)}) or be 1"
                )
        
        # Prepare multimodal inputs
        inputs = []
        for text, image in zip(texts, images):
            if image is not None:
                if not PIL_AVAILABLE:
                    raise RuntimeError(
                        "PIL/Pillow is required for image processing. "
                        "Install it with: pip install Pillow"
                    )
                # Multimodal: text + image
                input_item = {
                    "text": text,
                    "image": self._image_to_base64(image)
                }
            else:
                # Text only
                input_item = {"text": text}
            
            inputs.append(input_item)
        
        return self._get_multimodal_embeddings(inputs)
    
    def _get_text_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for text-only inputs (legacy method).
        
        Args:
            texts: List of text strings
        
        Returns:
            numpy array of embeddings
        """
        payload = {"input": texts}
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            embeddings = []
            for item in sorted(result["data"], key=lambda x: x["index"]):
                embeddings.append(item["embedding"])
            
            return np.array(embeddings, dtype=np.float32)
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error calling embedding API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Error parsing API response: {str(e)}")
    
    def _get_multimodal_embeddings(self, inputs: List[Dict[str, Any]]) -> np.ndarray:
        """
        Get embeddings for multimodal inputs (text + images).
        
        Args:
            inputs: List of input dictionaries with 'text' and optional 'image'
        
        Returns:
            numpy array of embeddings
        """
        payload = {"input": inputs}
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=60  # Longer timeout for images
            )
            response.raise_for_status()
            
            result = response.json()
            
            embeddings = []
            for item in sorted(result["data"], key=lambda x: x["index"]):
                embeddings.append(item["embedding"])
            
            return np.array(embeddings, dtype=np.float32)
            
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error calling embedding API: {str(e)}")
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Error parsing API response: {str(e)}")
    
    def get_embedding_dimension(self) -> int:
        """
        Get the dimension of the embedding vectors.
        
        Returns:
            Dimension of embedding vectors
        """
        test_embedding = self.get_embeddings("test")
        return test_embedding.shape[1]


if __name__ == "__main__":
    # Test the embedding client
    client = QwenEmbeddingClient()
    
    print("Testing Qwen3-VL Embedding Client\n")
    
    # Test single text
    print("1. Text-only embedding:")
    text = "The capital of China is Beijing."
    embedding = client.get_embeddings(text)
    print(f"   Shape: {embedding.shape}\n")
    
    # Test multiple texts
    print("2. Multiple text embeddings:")
    texts = ["The capital of China is Beijing.", "Gravity is a force"]
    embeddings = client.get_embeddings(texts)
    print(f"   Shape: {embeddings.shape}\n")
    
    # Get embedding dimension
    dim = client.get_embedding_dimension()
    print(f"3. Embedding dimension: {dim}\n")
    
    # Test with image (if PIL available)
    if PIL_AVAILABLE:
        print("4. Multimodal embedding (text + image):")
        print("   Note: Requires a test image to be available")
        print("   Example usage:")
        print("   ```python")
        print("   from PIL import Image")
        print("   img = Image.open('test.jpg')")
        print("   embedding = client.get_embeddings('A beautiful sunset', images=img)")
        print("   ```")
    else:
        print("4. PIL not available - install with: pip install Pillow")
    
    print("\nFor PDF support:")
    print("   from pdf_processor import PDFProcessor, pdf_page_to_multimodal_document")
    print("   processor = PDFProcessor()")
    print("   pages = processor.process_pdf('document.pdf')")
    print("   # Each page has both text and image for multimodal embedding")
