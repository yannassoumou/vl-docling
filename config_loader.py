"""
Configuration Loader for RAG System

Loads configuration from multiple sources with priority:
1. config.yaml (main configuration file)
2. Environment variables (.env)
3. Default values

Usage:
    from config_loader import load_config, get_config
    
    # Load configuration
    config = load_config()
    
    # Access values
    api_url = config['embedding']['api_url']
    top_k = config['retrieval']['top_k']
    
    # Or use helper
    from config_loader import get_config
    top_k = get_config('retrieval.top_k', default=5)
"""

import os
import yaml
from typing import Any, Dict, Optional
from pathlib import Path
from dotenv import load_dotenv


class ConfigLoader:
    """Configuration loader with multiple sources support."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config_path = config_path
        self.config = {}
        self._loaded = False
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from all sources.
        
        Returns:
            Complete configuration dictionary
        """
        if self._loaded:
            return self.config
        
        # Load environment variables first
        load_dotenv()
        
        # Load YAML configuration
        self.config = self._load_yaml()
        
        # Override with environment variables
        self._apply_env_overrides()
        
        self._loaded = True
        return self.config
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            print(f"Warning: Configuration file not found: {self.config_path}")
            print("Using default configuration")
            return self._get_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config or {}
        except Exception as e:
            print(f"Error loading configuration: {e}")
            print("Using default configuration")
            return self._get_default_config()
    
    def _apply_env_overrides(self):
        """Override configuration with environment variables."""
        # Embedding API
        if os.getenv('EMBEDDING_API_URL'):
            self.config.setdefault('embedding', {})['api_url'] = os.getenv('EMBEDDING_API_URL')
        
        # Reranker API
        if os.getenv('RERANKER_API_URL'):
            self.config.setdefault('reranker', {})['api_url'] = os.getenv('RERANKER_API_URL')
        
        if os.getenv('RERANKER_ENABLED'):
            enabled = os.getenv('RERANKER_ENABLED').lower() in ('true', '1', 'yes')
            self.config.setdefault('reranker', {})['enabled'] = enabled
        
        # Vector store type
        if os.getenv('VECTOR_STORE_TYPE'):
            self.config.setdefault('vector_store', {})['type'] = os.getenv('VECTOR_STORE_TYPE')
        
        # Milvus settings
        if os.getenv('MILVUS_HOST'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['host'] = os.getenv('MILVUS_HOST')
        
        if os.getenv('MILVUS_PORT'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['port'] = os.getenv('MILVUS_PORT')
        
        if os.getenv('MILVUS_USER'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['user'] = os.getenv('MILVUS_USER')
        
        if os.getenv('MILVUS_PASSWORD'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['password'] = os.getenv('MILVUS_PASSWORD')
        
        if os.getenv('MILVUS_DB_NAME'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['db_name'] = os.getenv('MILVUS_DB_NAME')
        
        if os.getenv('MILVUS_COLLECTION_NAME'):
            self.config.setdefault('vector_store', {}).setdefault('milvus', {})['collection_name'] = os.getenv('MILVUS_COLLECTION_NAME')
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'embedding': {
                'api_url': 'http://100.126.235.19:8888/v1/embeddings',
                'timeout': 60,
                'batch_size': 32
            },
            'reranker': {
                'enabled': False,
                'api_url': 'http://100.126.235.19:8888/v1/rerank',
                'rerank_top_k': 20,
                'final_top_k': 5
            },
            'document_processing': {
                'chunking': {
                    'chunk_size': 500,
                    'chunk_overlap': 50
                },
                'pdf': {
                    'dpi': 150,
                    'extract_text': True
                }
            },
            'retrieval': {
                'top_k': 5
            },
            'vector_store': {
                'type': 'faiss'
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., 'embedding.api_url')
            default: Default value if key not found
        
        Returns:
            Configuration value
        
        Example:
            api_url = config.get('embedding.api_url')
            top_k = config.get('retrieval.top_k', default=5)
        """
        if not self._loaded:
            self.load()
        
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path
            value: Value to set
        """
        if not self._loaded:
            self.load()
        
        keys = key_path.split('.')
        config = self.config
        
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        config[keys[-1]] = value
    
    def save(self, output_path: Optional[str] = None):
        """
        Save current configuration to YAML file.
        
        Args:
            output_path: Output file path (default: same as config_path)
        """
        output_path = output_path or self.config_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"Configuration saved to: {output_path}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def reload(self):
        """Reload configuration from sources."""
        self._loaded = False
        return self.load()
    
    def print_config(self, section: Optional[str] = None):
        """
        Print configuration in readable format.
        
        Args:
            section: Optional section to print (e.g., 'embedding')
        """
        if not self._loaded:
            self.load()
        
        config_to_print = self.config
        if section:
            config_to_print = self.config.get(section, {})
        
        print(yaml.dump(config_to_print, default_flow_style=False, sort_keys=False))


# Global configuration instance
_config_loader = None


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    global _config_loader
    _config_loader = ConfigLoader(config_path)
    return _config_loader.load()


def get_config(key_path: str = None, default: Any = None) -> Any:
    """
    Get configuration value.
    
    Args:
        key_path: Dot-separated key path (e.g., 'embedding.api_url')
                 If None, returns entire configuration
        default: Default value if key not found
    
    Returns:
        Configuration value
    """
    global _config_loader
    if _config_loader is None:
        load_config()
    
    if key_path is None:
        return _config_loader.config
    
    return _config_loader.get(key_path, default)


def set_config(key_path: str, value: Any):
    """
    Set configuration value.
    
    Args:
        key_path: Dot-separated key path
        value: Value to set
    """
    global _config_loader
    if _config_loader is None:
        load_config()
    
    _config_loader.set(key_path, value)


def save_config(output_path: Optional[str] = None):
    """
    Save configuration to file.
    
    Args:
        output_path: Output file path
    """
    global _config_loader
    if _config_loader is None:
        load_config()
    
    _config_loader.save(output_path)


def print_config(section: Optional[str] = None):
    """
    Print configuration.
    
    Args:
        section: Optional section to print
    """
    global _config_loader
    if _config_loader is None:
        load_config()
    
    _config_loader.print_config(section)


if __name__ == "__main__":
    # Example usage
    print("=" * 80)
    print("Configuration Loader Example")
    print("=" * 80)
    print()
    
    # Load configuration
    print("Loading configuration...")
    config = load_config()
    print("✓ Configuration loaded\n")
    
    # Access values
    print("Example values:")
    print(f"  Embedding API URL: {get_config('embedding.api_url')}")
    print(f"  Retrieval Top-K: {get_config('retrieval.top_k')}")
    print(f"  Chunk Size: {get_config('document_processing.chunking.chunk_size')}")
    print(f"  PDF DPI: {get_config('document_processing.pdf.dpi')}")
    print(f"  Reranker Enabled: {get_config('reranker.enabled')}")
    print()
    
    # Print sections
    print("Embedding Configuration:")
    print_config('embedding')
    
    print("\nRetrieval Configuration:")
    print_config('retrieval')
