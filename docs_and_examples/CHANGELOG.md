# Changelog

All notable changes to the Qwen3VL RAG System.

## [2.3.0] - 2026-01-16

### Added - Comprehensive Configuration System

#### Centralized Configuration
- **`config.yaml`** - Main configuration file with 100+ parameters
  - Embedding API settings
  - Reranker API settings (prepared for Qwen3-VL-Reranker)
  - Document processing (chunking, PDF)
  - Retrieval configuration
  - Vector store settings (FAISS + Milvus)
  - Performance tuning
  - Logging and monitoring
  - Multimodal settings
  - Advanced features

- **`config_loader.py`** - Configuration management system
  - Load from YAML + environment variables
  - Python API with dot-notation access
  - Save/reload capabilities
  - Default fallbacks

- **`env.example`** - Environment variable template
  - Override config.yaml per environment
  - Reranker endpoint configuration
  - Production/development settings

#### Documentation
- **`CONFIG_GUIDE.md`** - Complete configuration guide
  - Parameter explanations
  - Tuning tips and best practices
  - Common scenarios
  - Troubleshooting

- **`CONFIG_SUMMARY.md`** - Quick configuration overview

#### Reranker Preparation
- Configuration ready for Qwen3-VL-Reranker integration
- Two-stage retrieval support (embedding + reranking)
- Just set `reranker.enabled: true` when endpoint available

#### Features
- ✅ 100+ adjustable parameters
- ✅ YAML-based configuration (human-readable)
- ✅ Environment variable overrides
- ✅ Production and development settings
- ✅ Performance tuning options
- ✅ Reranker integration prepared
- ✅ Comprehensive documentation

### Dependencies
- Added `PyYAML==6.0.1` for YAML parsing

## [2.2.0] - 2026-01-16

### Added - Multimodal PDF Support

#### PDF Processing with Visual Understanding
- **`pdf_processor.py`** - Complete PDF processing with page-to-image conversion
  - Converts each PDF page to high-quality images
  - Extracts text from PDFs
  - Configurable DPI settings (72-300)
  - Batch processing support

- **`multimodal_rag.py`** - Multimodal RAG engine
  - Process PDFs with both text AND visual understanding
  - Leverages Qwen3-VL-Embedding's multimodal capabilities
  - Three processing modes: multimodal, text-only, image-only
  - Query with text or text+image

- **`example_pdf.py`** - PDF processing example
  - Demonstrates multimodal PDF processing
  - Shows visual understanding in action

#### New Documentation
- `PDF_GUIDE.md` - Complete guide for PDF processing
- `sample_pdfs/` directory - Place for example PDFs

#### Features
- ✅ Page-by-page PDF conversion to images
- ✅ Multimodal embeddings (text + visual content)
- ✅ Understanding of charts, diagrams, and visual elements
- ✅ Flexible processing modes
- ✅ Configurable DPI for quality vs performance
- ✅ Batch processing for large PDFs
- ✅ Integration with existing FAISS/Milvus infrastructure

#### Enhanced Components
- Updated `embedding_client.py` to support multimodal inputs
- Added image support with base64 encoding
- New launcher command: `example-pdf`

#### Dependencies
- Added `PyMuPDF==1.23.26` for PDF processing
- Added `Pillow==10.2.0` for image handling

### Based On
- [Qwen3-VL-Embedding-8B](https://huggingface.co/Qwen/Qwen3-VL-Embedding-8B)
- Supports text, images, and multimodal combinations

## [2.1.0] - 2026-01-16

### Added - Launcher Scripts

#### Easy-to-Use Launchers
- **`run.sh`** - Linux/Mac/WSL launcher with auto-setup
- **`run.bat`** - Windows Command Prompt launcher
- **`run.ps1`** - Windows PowerShell launcher (recommended for Windows)
- **`setup-milvus.sh`** - Automated Milvus setup for Linux/Mac
- **`setup-milvus.bat`** - Automated Milvus setup for Windows CMD
- **`setup-milvus.ps1`** - Automated Milvus setup for Windows PowerShell

#### New Documentation
- `LAUNCHER_GUIDE.md` - Complete guide for launcher scripts
- `QUICK_REFERENCE.md` - One-page cheat sheet
- `START_HERE.md` - Entry point for new users

#### Features
- ✅ Automatic virtual environment creation
- ✅ Automatic dependency installation
- ✅ No manual setup required
- ✅ Cross-platform support
- ✅ Simplified commands (e.g., `.\run.ps1 interactive`)
- ✅ One-command Milvus setup

### Changed
- Enhanced README with launcher script documentation
- Updated QUICKSTART with launcher options
- Improved new user experience

## [2.0.0] - 2026-01-16

### Added - Vector Store Flexibility

#### New Features
- **Milvus Support**: Added full support for Milvus vector database
  - Local Milvus via Docker
  - Remote Milvus server support
  - Automatic persistence
  - Scalable to billions of vectors

- **Vector Store Factory**: New factory pattern for creating vector stores
  - `vector_store_factory.py` - Factory for creating stores
  - Easy switching between FAISS and Milvus
  - Extensible for future store types

- **Configuration System**: Enhanced configuration options
  - Environment variables via `.env` file
  - Command-line store selection (`--store` flag)
  - Programmatic configuration
  - Multiple Milvus configuration options (host, port, auth, etc.)

#### New Files
- `milvus_store.py` - Milvus vector store implementation
- `vector_store_factory.py` - Factory for creating vector stores
- `docker-compose.yml` - Docker Compose for local Milvus
- `MILVUS_SETUP.md` - Comprehensive Milvus setup guide
- `VECTOR_STORES_GUIDE.md` - Vector stores configuration guide
- `example_milvus.py` - Milvus usage examples

#### Enhanced Files
- `config.py` - Added Milvus configuration options
- `rag_engine.py` - Support for multiple vector store types
- `main.py` - Added `--store` command-line option
- `requirements.txt` - Added `pymilvus` dependency
- `README.md` - Updated with Milvus documentation
- `QUICKSTART.md` - Added Milvus quick start

#### Configuration Options
```bash
# New environment variables
VECTOR_STORE_TYPE=faiss|milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_USER=username
MILVUS_PASSWORD=password
MILVUS_DB_NAME=default
MILVUS_COLLECTION_NAME=rag_documents
MILVUS_INDEX_TYPE=IVF_FLAT
MILVUS_METRIC_TYPE=L2
```

### Changed
- RAGEngine now accepts `store_type` parameter
- Vector stores can be created via factory function
- CLI supports `--store` flag for runtime selection

### Migration Guide

#### For Existing Users
Your existing FAISS-based setup will continue to work without changes. FAISS remains the default.

#### To Use Milvus
1. Start Milvus: `docker-compose up -d`
2. Set in `.env`: `VECTOR_STORE_TYPE=milvus`
3. Use as normal: `python main.py ingest --directory ./docs`

#### To Migrate Data
```python
# Load from FAISS
rag_old = RAGEngine(store_type='faiss')
rag_old.load()

# Save to Milvus
rag_new = RAGEngine(store_type='milvus')
rag_new.vector_store.add_chunks(rag_old.vector_store.chunks)
```

## [1.0.0] - 2026-01-16

### Initial Release

#### Core Features
- **Embedding Client**: Integration with Qwen3VL embedding API
- **Document Processing**: Text chunking with configurable size and overlap
- **FAISS Vector Store**: Fast local vector similarity search
- **RAG Engine**: Complete retrieval-augmented generation pipeline
- **CLI Application**: Command-line interface for all operations
- **Python API**: Programmatic access for integration

#### Files
- `embedding_client.py` - Qwen3VL API client
- `document_processor.py` - Document loading and chunking
- `vector_store.py` - FAISS vector store
- `rag_engine.py` - Main RAG engine
- `main.py` - CLI application
- `example.py` - Usage examples
- `setup.py` - Setup script
- `config.py` - Configuration
- `requirements.txt` - Dependencies
- `README.md` - Documentation
- `QUICKSTART.md` - Quick start guide

#### Sample Documents
- `sample_docs/python_basics.txt`
- `sample_docs/machine_learning.txt`
- `sample_docs/neural_networks.txt`
- `sample_docs/rag_systems.txt`

---

## Version History

- **2.0.0** - Added Milvus support and vector store flexibility
- **1.0.0** - Initial release with FAISS support
