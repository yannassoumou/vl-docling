# Query Results Saving Guide

## Overview

The query result saving system automatically saves both raw retrieval and reranked results to disk for each query. This enables:

1. **Evaluation**: Compare raw vector search vs reranked results
2. **LLM Integration**: Load reranked results directly without re-running retrieval
3. **Analysis**: Analyze retrieval patterns and quality over time
4. **Debugging**: Inspect what the system retrieved for each query

## Configuration

Enable query result saving in `config.yaml`:

```yaml
query_results:
  # Enable saving query results to disk
  save_results: true
  
  # Output directory for query results
  output_dir: "query_results"
```

## Directory Structure

Each query creates a timestamped folder:

```
query_results/
├── 20260117_143022_What_is_machine_learning/
│   ├── query_metadata.json       # Query info and counts
│   ├── raw_retrieval.json        # Raw vector search results
│   └── reranked_results.json     # Reranked results (if reranker enabled)
├── 20260117_143145_How_does_RAG_work/
│   ├── query_metadata.json
│   ├── raw_retrieval.json
│   └── reranked_results.json
└── ...
```

## File Formats

### query_metadata.json

```json
{
  "query": "What is machine learning?",
  "timestamp": "2026-01-17T14:30:22.123456",
  "raw_result_count": 20,
  "reranked_result_count": 5,
  "reranker_used": true,
  "rerank_top_k": 20,
  "final_top_k": 5
}
```

### raw_retrieval.json

```json
{
  "query": "What is machine learning?",
  "timestamp": "2026-01-17T14:30:22.123456",
  "result_count": 20,
  "results": [
    {
      "content": "Machine learning is a subset of AI...",
      "score": 0.9523,
      "chunk_id": 42,
      "metadata": {
        "source": "ml_intro.pdf",
        "page": 1,
        "chunk_index": 0
      }
    },
    ...
  ]
}
```

### reranked_results.json

```json
{
  "query": "What is machine learning?",
  "timestamp": "2026-01-17T14:30:22.123456",
  "result_count": 5,
  "results": [
    {
      "content": "Machine learning is a subset of AI...",
      "score": 0.9523,
      "rerank_score": 0.9876,
      "original_rank": 1,
      "new_rank": 1,
      "chunk_id": 42,
      "metadata": {
        "source": "ml_intro.pdf",
        "page": 1
      }
    },
    ...
  ]
}
```

## Usage

### 1. Query with Result Saving (Automatic)

If enabled in config, results are saved automatically:

```bash
# Windows
.\run.ps1 query "What is machine learning?"

# Linux/Mac
./run.sh query "What is machine learning?"
```

### 2. Override Config Settings

Force save or disable saving for a specific query:

```bash
# Force save (even if disabled in config)
python main.py query "What is RAG?" --save-results

# Disable save (even if enabled in config)
python main.py query "What is RAG?" --no-save-results
```

### 3. List Saved Queries

```bash
python main.py list-queries
```

Output:
```
================================================================================
SAVED QUERY RESULTS
================================================================================
Total saved queries: 3

1. [2026-01-17T14:30:22.123456]
   Query: What is machine learning?
   Results: 20 raw, 5 reranked
   Folder: 20260117_143022_What_is_machine_learning

2. [2026-01-17T14:31:45.789012]
   Query: How does RAG work?
   Results: 20 raw, 5 reranked
   Folder: 20260117_143145_How_does_RAG_work

================================================================================
```

### 4. Load and Display Saved Results

```bash
# Load by folder name
python main.py load-query 20260117_143022_What_is_machine_learning

# Load with full content preview
python main.py load-query 20260117_143022_What_is_machine_learning --show-content
```

Output:
```
================================================================================
LOADED QUERY RESULTS
================================================================================
Query: What is machine learning?
Timestamp: 2026-01-17T14:30:22.123456
Reranker used: Yes
================================================================================

Raw Retrieval Results (20 results):
--------------------------------------------------------------------------------
1. Score: 0.9523 | ml_intro.pdf
2. Score: 0.9401 | dl_basics.pdf
3. Score: 0.9287 | neural_networks.pdf
...

Reranked Results (5 results):
--------------------------------------------------------------------------------
1. (=) Rerank: 0.9876 | Vector: 0.9523 | ml_intro.pdf
2. (+3) Rerank: 0.9654 | Vector: 0.9102 | ai_overview.pdf
3. (-1) Rerank: 0.9543 | Vector: 0.9401 | dl_basics.pdf
...
```

## Use Cases

### 1. Evaluation and Comparison

Compare raw vs reranked results to evaluate reranker effectiveness:

```python
from query_result_saver import QueryResultSaver

saver = QueryResultSaver()
results = saver.load_query_results("query_results/20260117_143022_What_is_machine_learning")

raw_results = results['raw']['results']
reranked_results = results['reranked']['results']

# Compare top result sources
print("Raw top result:", raw_results[0]['metadata']['source'])
print("Reranked top result:", reranked_results[0]['metadata']['source'])

# Analyze rank changes
for result in reranked_results:
    rank_change = result['original_rank'] - result['new_rank']
    if rank_change > 0:
        print(f"Promoted: {result['metadata']['source']} (+{rank_change})")
```

### 2. LLM Integration (Reuse Reranked Results)

Load reranked results directly for LLM without re-running retrieval:

```python
from query_result_saver import QueryResultSaver
import json

saver = QueryResultSaver()

# Load pre-computed reranked results
results = saver.load_query_results("query_results/20260117_143022_What_is_machine_learning")
reranked = results['reranked']['results']

# Build context for LLM
context = "\n\n---\n\n".join([
    f"[Source: {r['metadata']['source']}]\n{r['content']}"
    for r in reranked
])

# Send to LLM
query = results['metadata']['query']
prompt = f"Question: {query}\n\nContext:\n{context}\n\nAnswer:"

# Call your LLM API here
# response = llm_api.generate(prompt)
```

### 3. Batch Evaluation

Evaluate retrieval quality across multiple queries:

```python
from query_result_saver import QueryResultSaver

saver = QueryResultSaver()
all_queries = saver.list_saved_queries()

for query_info in all_queries:
    results = saver.load_query_results(query_info['path'])
    
    # Calculate metrics
    raw_count = results['raw']['result_count']
    reranked_count = results['reranked']['result_count'] if 'reranked' in results else 0
    
    print(f"Query: {query_info['query'][:50]}")
    print(f"  Raw: {raw_count}, Reranked: {reranked_count}")
    
    # Analyze rank changes
    if 'reranked' in results:
        reranked_results = results['reranked']['results']
        promoted = sum(1 for r in reranked_results if r.get('original_rank', 0) > r.get('new_rank', 0))
        print(f"  Promoted results: {promoted}/{len(reranked_results)}")
```

### 4. Export for External Analysis

Export to CSV for analysis in Excel/Pandas:

```python
import csv
from query_result_saver import QueryResultSaver

saver = QueryResultSaver()
results = saver.load_query_results("query_results/20260117_143022_What_is_machine_learning")

# Export reranked results to CSV
with open('reranked_results.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Rank', 'Original Rank', 'Vector Score', 'Rerank Score', 'Source', 'Content Preview'])
    
    for result in results['reranked']['results']:
        writer.writerow([
            result.get('new_rank', ''),
            result.get('original_rank', ''),
            result.get('score', ''),
            result.get('rerank_score', ''),
            result['metadata'].get('source', ''),
            result['content'][:100]
        ])
```

## Programmatic Access

Use the `QueryResultSaver` class directly in your code:

```python
from query_result_saver import QueryResultSaver

# Initialize
saver = QueryResultSaver(output_dir="my_query_results")

# Save results manually
saver.save_query_results(
    query="What is machine learning?",
    raw_results=raw_results,
    reranked_results=reranked_results,
    metadata={'custom_field': 'value'}
)

# Load results
results = saver.load_query_results("path/to/query/folder")

# List all saved queries
queries = saver.list_saved_queries()
for q in queries:
    print(f"{q['timestamp']}: {q['query']}")
```

## Best Practices

1. **Enable for Production**: Always enable in production to track retrieval quality
2. **Regular Cleanup**: Periodically archive or delete old query results
3. **Version Control**: Don't commit `query_results/` to git (already in `.gitignore`)
4. **Analysis**: Regularly review saved results to identify retrieval issues
5. **LLM Caching**: Use saved reranked results as a cache for repeated queries

## Troubleshooting

### Results Not Saving

Check configuration:
```bash
# Verify config
grep -A 3 "query_results:" config.yaml

# Check if directory exists and is writable
ls -la query_results/
```

### Cannot Load Results

Ensure the folder structure is correct:
```bash
# Check folder contents
ls query_results/20260117_143022_What_is_machine_learning/

# Should contain:
# - query_metadata.json
# - raw_retrieval.json
# - reranked_results.json (if reranker was used)
```

### Large Disk Usage

Query results can accumulate quickly. Clean up periodically:

```bash
# Remove results older than 30 days (Linux/Mac)
find query_results/ -type d -mtime +30 -exec rm -rf {} +

# Or manually delete old folders
rm -rf query_results/20260101_*
```

## See Also

- [RERANKER_GUIDE.md](RERANKER_GUIDE.md) - Reranker configuration and usage
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick command reference
- [CONFIG_GUIDE.md](CONFIG_GUIDE.md) - Full configuration guide
