#!/usr/bin/env python3
"""
Setup script for the Qwen3VL RAG System.

This script helps you set up and test the RAG system.
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def check_venv():
    """Check if running in a virtual environment."""
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("✓ Running in virtual environment")
    else:
        print("⚠ Warning: Not running in a virtual environment")
        print("  It's recommended to use a virtual environment")
        print("  Run: python -m venv .venv")
        print("  Then activate it before running setup")
    return in_venv


def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        return False


def test_imports():
    """Test if required packages can be imported."""
    print("\nTesting imports...")
    packages = ['requests', 'numpy', 'faiss']
    
    all_ok = True
    for package in packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - Failed to import")
            all_ok = False
    
    return all_ok


def test_embedding_api():
    """Test connection to the embedding API."""
    print("\nTesting embedding API connection...")
    try:
        from embedding_client import QwenEmbeddingClient
        
        client = QwenEmbeddingClient()
        embedding = client.get_embeddings("test")
        
        print(f"✓ API connection successful")
        print(f"  Embedding dimension: {embedding.shape[1]}")
        return True
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        print("\nPlease check:")
        print("  1. The embedding server is running")
        print("  2. The URL in config.py is correct")
        print("  3. You can access http://100.126.235.19:8888/v1/embeddings")
        return False


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    dirs = ['vector_store']
    
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ {dir_name}/")
    
    return True


def run_example():
    """Ask if user wants to run the example."""
    print("\n" + "=" * 80)
    response = input("Would you like to run the example script? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\nRunning example.py...\n")
        try:
            subprocess.check_call([sys.executable, "example.py"])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error running example: {e}")
            return False
    return True


def main():
    """Run the setup process."""
    print("=" * 80)
    print("Qwen3VL RAG System Setup")
    print("=" * 80)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Checking virtual environment", check_venv),
        ("Installing dependencies", install_dependencies),
        ("Testing imports", test_imports),
        ("Testing embedding API", test_embedding_api),
        ("Creating directories", create_directories),
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"\n✗ Setup failed at: {step_name}")
            print("\nPlease fix the issue and run setup again.")
            return 1
    
    print("\n" + "=" * 80)
    print("✓ Setup completed successfully!")
    print("=" * 80)
    
    print("\nNext steps:")
    print("  1. Ingest some documents:")
    print("     python main.py ingest --directory ./sample_docs")
    print("\n  2. Query the system:")
    print("     python main.py query \"What is Python?\"")
    print("\n  3. Try interactive mode:")
    print("     python main.py interactive")
    print("\n  4. See all options:")
    print("     python main.py --help")
    
    run_example()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
