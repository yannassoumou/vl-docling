# Configuration Guide

Complete guide for configuring your RAG system for optimal performance.

## Configuration Files

### 1. `config.yaml` - Main Configuration File ⭐ RECOMMENDED

The primary configuration file with all adjustable parameters.

**Location**: `config.yaml` (project root)

**Format**: YAML (human-readable, easy to edit)

**Sections**:
- 🔌 **Embedding API** - Qwen3-VL-Embedding endpoint settings
- 🎯 **Reranker API** - Qwen3-VL-Reranker endpoint (future)
- 📄 **Document Processing** - Chunking and PDF settings
- 🔍 **Retrieval** - Search and ranking parameters
- 💾 **Vector Store** - FAISS and Milvus configuration
- ⚙️ **RAG Engine** - Context formatting and caching
- 🚀 **Performance** - Parallel processing and GPU settings
- 📊 **Logging** - Debug and monitoring options
- 🖼️ **Multimodal** - Image and video processing
- 🔬 **Advanced** - Experimental features

### 2. `.env` - Environment Variables

Override specific settings without editing config.yaml.

**Location**: `.env` (project root, create from `.env.example`)

**Use for**:
- API endpoints (different per environment)
- Credentials (never commit to git)
- Environment-specific overrides

### 3. `config.py` - Legacy Python Config

**Status**: Deprecated in favor of config.yaml

**Migration**: All settings now in config.yaml

## Quick Start

### 1. Use Default Configuration

No configuration needed! The system works out of the box:

```powershell
.\run.ps1 example
```

### 2. Basic Customization

Edit `config.yaml` for your needs:

```yaml
# Adjust retrieval settings
retrieval:
  top_k: 10  # Return more results

# Adjust PDF quality
document_processing:
  pdf:
    dpi: 200  # Higher quality
```

### 3. Environment-Specific Settings

Create `.env` file:

```bash
# Development environment
EMBEDDING_API_URL=http://localhost:8888/v1/embeddings
VECTOR_STORE_TYPE=faiss

# Production environment
EMBEDDING_API_URL=http://production-server:8888/v1/embeddings
VECTOR_STORE_TYPE=milvus
MILVUS_HOST=milvus-cluster.example.com
```

## Configuration Sections

### 🔌 Embedding API

```yaml
embedding:
  api_url: "http://100.126.235.19:8888/v1/embeddings"
  timeout: 60
  batch_size: 32
  max_retries: 3
```

**Key Parameters**:
- `api_url`: Your Qwen3-VL-Embedding endpoint
- `timeout`: API timeout in seconds (increase for slow networks)
- `batch_size`: Documents per API call (higher = faster but more memory)
- `max_retries`: Retry failed requests

**Tuning Tips**:
- Increase `batch_size` for faster processing (if API supports it)
- Increase `timeout` for large images or slow networks
- Adjust `max_retries` based on API reliability

### 🎯 Reranker API (Two-Stage Retrieval)

```yaml
reranker:
  enabled: false  # Set to true when endpoint is available
  api_url: "http://100.126.235.19:8888/v1/rerank"
  rerank_top_k: 20  # Retrieve this many for reranking
  final_top_k: 5    # Return this many after reranking
```

**How It Works**:
1. **Stage 1**: Fast embedding search retrieves `rerank_top_k` candidates
2. **Stage 2**: Reranker refines results to `final_top_k` best matches

**Benefits**:
- Higher accuracy than embedding-only search
- Captures fine-grained relevance
- Industry best practice for production RAG

**When to Enable**:
- ✅ When you have Qwen3-VL-Reranker endpoint
- ✅ When accuracy is more important than speed
- ✅ For complex queries requiring nuanced understanding

**Tuning Tips**:
- Set `rerank_top_k` = 2-4× your desired `final_top_k`
- Typical: `rerank_top_k: 20`, `final_top_k: 5`
- Higher `rerank_top_k` = more accurate but slower

### 📄 Document Processing

#### Chunking Strategy

```yaml
document_processing:
  chunking:
    chunk_size: 500
    chunk_overlap: 50
    min_chunk_size: 50
    max_chunk_size: 2000
    respect_sentence_boundary: true
```

**Key Parameters**:
- `chunk_size`: Target chunk size in characters
- `chunk_overlap`: Overlap between consecutive chunks
- `respect_sentence_boundary`: Try to break at sentence ends

**Tuning Guide**:

| Chunk Size | Use Case | Pros | Cons |
|------------|----------|------|------|
| 200-300 | Short answers, Q&A | Precise retrieval | May lose context |
| 400-600 | **General purpose** ⭐ | Balanced | - |
| 800-1200 | Long documents, context-heavy | More context | Less precise |

**Overlap Guidelines**:
- 10-20% of chunk_size (typical: 50-100 chars)
- Higher overlap = more context but more storage

**Best Practices**:
```yaml
# For precise Q&A
chunk_size: 300
chunk_overlap: 30

# For narrative text
chunk_size: 800
chunk_overlap: 80

# For technical docs
chunk_size: 500
chunk_overlap: 50
```

#### PDF Processing

```yaml
document_processing:
  pdf:
    dpi: 150
    extract_text: true
    image_format: "PNG"
    default_mode: "multimodal"
```

**DPI Settings**:

| DPI | Quality | Speed | Use Case |
|-----|---------|-------|----------|
| 72  | Low | Fast | Text-only docs |
| 150 | Good | Medium | **Recommended** ⭐ |
| 200 | High | Slow | Charts/diagrams |
| 300 | Very High | Very Slow | Print quality |

**Modes**:
- `multimodal`: Text + images (best for visual content)
- `text-only`: Faster, text-heavy documents
- `image-only`: Scanned documents

### 🔍 Retrieval Configuration

```yaml
retrieval:
  top_k: 5
  min_similarity_score: 0.0
  enable_diversity: false
  diversity_penalty: 0.3
```

**Key Parameters**:
- `top_k`: Number of results to return
- `min_similarity_score`: Filter out low-relevance results
- `enable_diversity`: Promote diverse results

**Tuning for Different Scenarios**:

```yaml
# High precision (fewer, better results)
top_k: 3
min_similarity_score: 0.5

# High recall (more results, catch everything)
top_k: 10
min_similarity_score: 0.0

# Diverse results (avoid similar chunks)
top_k: 5
enable_diversity: true
diversity_penalty: 0.5
```

### 💾 Vector Store

#### FAISS Configuration

```yaml
vector_store:
  type: "faiss"
  faiss:
    store_path: "vector_store"
    index_type: "Flat"  # or IVF, HNSW
```

**Index Types**:

| Type | Speed | Accuracy | Memory | Use Case |
|------|-------|----------|--------|----------|
| Flat | Slow | Perfect | High | < 10K docs |
| IVF | Fast | Good | Medium | 10K-1M docs |
| HNSW | Very Fast | Excellent | High | Speed-critical |

#### Milvus Configuration

```yaml
vector_store:
  type: "milvus"
  milvus:
    host: "localhost"
    port: 19530
    collection_name: "rag_documents"
    index_type: "IVF_FLAT"
    metric_type: "L2"
```

**Index Types for Milvus**:
- `IVF_FLAT`: Balanced (recommended)
- `IVF_SQ8`: Memory-efficient
- `HNSW`: Fastest search
- `IVF_PQ`: Largest datasets

**Metric Types**:
- `L2`: Euclidean distance (default)
- `IP`: Inner product
- `COSINE`: Cosine similarity (good for text)

### ⚙️ RAG Engine

```yaml
rag:
  max_context_length: 4000
  context_format:
    include_source: true
    include_page_numbers: true
    chunk_separator: "\n---\n"
```

**Context Formatting**:
- `max_context_length`: Max characters for LLM context
- `include_source`: Show source file names
- `include_page_numbers`: Show page numbers (PDFs)

### 🚀 Performance Tuning

```yaml
performance:
  parallel:
    enabled: true
    num_workers: 0  # 0 = auto (CPU cores)
    batch_size: 32
  
  memory:
    max_memory_gb: 0  # 0 = unlimited
    memory_threshold: 80
  
  gpu:
    enabled: false
    device_id: 0
```

**Optimization Tips**:

**For Speed**:
```yaml
parallel:
  enabled: true
  num_workers: 8  # or CPU core count
  batch_size: 64
```

**For Memory Constraints**:
```yaml
memory:
  max_memory_gb: 4
  memory_threshold: 70
performance:
  parallel:
    batch_size: 16  # Smaller batches
```

**For GPU Acceleration**:
```yaml
gpu:
  enabled: true
  device_id: 0
```

## Loading Configuration

### Python API

```python
from config_loader import load_config, get_config

# Load all configuration
config = load_config()

# Access specific values
api_url = get_config('embedding.api_url')
top_k = get_config('retrieval.top_k', default=5)
chunk_size = get_config('document_processing.chunking.chunk_size')

# Set values
from config_loader import set_config, save_config

set_config('retrieval.top_k', 10)
save_config()  # Save to config.yaml
```

### Using with RAG Components

```python
from config_loader import get_config
from multimodal_rag import MultimodalRAGEngine

# Load configuration
pdf_dpi = get_config('document_processing.pdf.dpi')
top_k = get_config('retrieval.top_k')
vector_store_type = get_config('vector_store.type')

# Initialize with config
rag = MultimodalRAGEngine(
    pdf_dpi=pdf_dpi,
    top_k=top_k,
    vector_store_type=vector_store_type
)
```

## Common Scenarios

### Scenario 1: High-Quality PDF Processing

```yaml
document_processing:
  pdf:
    dpi: 200
    default_mode: "multimodal"

retrieval:
  top_k: 3
  min_similarity_score: 0.4
```

### Scenario 2: Fast Text Processing

```yaml
document_processing:
  chunking:
    chunk_size: 300
    chunk_overlap: 30
  pdf:
    dpi: 100
    default_mode: "text-only"

retrieval:
  top_k: 10
```

### Scenario 3: Production with Reranker

```yaml
reranker:
  enabled: true
  rerank_top_k: 20
  final_top_k: 5

retrieval:
  top_k: 20  # Must match rerank_top_k

vector_store:
  type: "milvus"
  milvus:
    index_type: "HNSW"
```

### Scenario 4: Large-Scale Processing

```yaml
performance:
  parallel:
    enabled: true
    num_workers: 16
    batch_size: 64

vector_store:
  type: "milvus"
  milvus:
    index_type: "IVF_PQ"

document_processing:
  chunking:
    chunk_size: 400
```

## Environment-Specific Configurations

### Development

```yaml
# config.dev.yaml
logging:
  level: "DEBUG"
  log_api_calls: true

development:
  debug: true
  verbose: true
```

### Production

```yaml
# config.prod.yaml
logging:
  level: "WARNING"
  log_api_calls: false

performance:
  parallel:
    enabled: true
    num_workers: 32

vector_store:
  type: "milvus"
```

## Validation

Test your configuration:

```python
from config_loader import load_config, print_config

# Load and validate
config = load_config()

# Print specific sections
print_config('embedding')
print_config('retrieval')
print_config('reranker')
```

## Best Practices

1. **Start with defaults** - They work well for most cases
2. **Use config.yaml** for permanent settings
3. **Use .env** for environment-specific overrides
4. **Version control config.yaml** but not .env
5. **Document your changes** with comments in YAML
6. **Test after changes** - especially performance settings
7. **Keep .env.example updated** for team members

## Troubleshooting

### Configuration Not Loading

```python
from config_loader import load_config

try:
    config = load_config('config.yaml')
    print("✓ Configuration loaded")
except Exception as e:
    print(f"✗ Error: {e}")
```

### Invalid Values

Check YAML syntax:
```bash
# Online YAML validator
# or use Python
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
```

### Environment Variables Not Working

```python
import os
print(f"EMBEDDING_API_URL: {os.getenv('EMBEDDING_API_URL')}")
print(f"VECTOR_STORE_TYPE: {os.getenv('VECTOR_STORE_TYPE')}")
```

## Summary

✅ **config.yaml** - Main configuration (all settings)  
✅ **.env** - Environment-specific overrides  
✅ **config_loader.py** - Python API for config access  
✅ **Prepared for reranker** - Just set `reranker.enabled: true`  

**Edit config.yaml and restart your application!**

---

**Next**: See [README.md](README.md) for full documentation
