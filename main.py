#!/usr/bin/env python3
"""
Main CLI application for the Qwen3VL RAG System.
"""

import argparse
import sys
from pathlib import Path

from rag_engine import RAGEngine, format_rag_response


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3VL RAG System - Retrieval-Augmented Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a single file
  python main.py ingest --file document.txt
  
  # Ingest a directory
  python main.py ingest --directory ./docs
  
  # Use Milvus instead of FAISS
  python main.py --store milvus ingest --directory ./docs
  
  # Query the system
  python main.py query "What is machine learning?"
  
  # Query with more results
  python main.py query "Explain Python" --top-k 10
  
  # Show statistics
  python main.py stats
  
  # Clear the vector store
  python main.py clear
        """
    )
    
    # Global arguments
    parser.add_argument(
        '--store',
        type=str,
        choices=['faiss', 'milvus'],
        help='Vector store type (faiss or milvus). Overrides config/env setting.'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest documents into the RAG system')
    ingest_group = ingest_parser.add_mutually_exclusive_group(required=True)
    ingest_group.add_argument('--file', type=str, help='Path to a single file to ingest')
    ingest_group.add_argument('--directory', type=str, help='Path to a directory to ingest (recursive by default)')
    ingest_group.add_argument('--text', type=str, help='Text string to ingest')
    ingest_parser.add_argument('--extensions', type=str, nargs='+', 
                              help='File extensions to include (for directory ingestion)')
    ingest_parser.add_argument('--no-recursive', action='store_true',
                              help='Do not recursively search subdirectories')
    
    # Query command
    query_parser = subparsers.add_parser('query', help='Query the RAG system')
    query_parser.add_argument('question', type=str, help='The question to ask')
    query_parser.add_argument('--top-k', type=int, default=5, help='Number of documents to retrieve')
    query_parser.add_argument('--context-only', action='store_true', 
                            help='Only show context without full formatting')
    query_parser.add_argument('--verbose', action='store_true',
                            help='Show detailed reranking process (before/after scores)')
    query_parser.add_argument('--save-results', action='store_true', default=None,
                            help='Save query results to disk (overrides config)')
    query_parser.add_argument('--no-save-results', action='store_true',
                            help='Do not save query results (overrides config)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics about the RAG system')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear the vector store')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive query mode')
    interactive_parser.add_argument('--top-k', type=int, default=5, help='Number of documents to retrieve')
    
    # List saved queries command
    subparsers.add_parser('list-queries', help='List all saved query results')
    
    # Load query results command
    load_query_parser = subparsers.add_parser('load-query', help='Load and display saved query results')
    load_query_parser.add_argument('folder', type=str, help='Query results folder name or path')
    load_query_parser.add_argument('--show-content', action='store_true',
                                   help='Show full content of results')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize RAG engine with specified store type
    rag = RAGEngine(
        store_type=args.store if hasattr(args, 'store') else None
    )
    
    # Load existing vector store if available
    if args.command != 'clear':
        rag.load()
    
    # Execute command
    if args.command == 'ingest':
        handle_ingest(rag, args)
    elif args.command == 'query':
        handle_query(rag, args)
    elif args.command == 'stats':
        handle_stats(rag)
    elif args.command == 'clear':
        handle_clear(rag)
    elif args.command == 'interactive':
        handle_interactive(rag, args)
    elif args.command == 'list-queries':
        handle_list_queries(rag)
    elif args.command == 'load-query':
        handle_load_query(rag, args)
    else:
        parser.print_help()
        sys.exit(1)


def handle_ingest(rag: RAGEngine, args):
    """Handle document ingestion."""
    print("Starting ingestion...")
    
    if args.file:
        if not Path(args.file).exists():
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        rag.ingest_file(args.file)
        print(f"Successfully ingested file: {args.file}")
    
    elif args.directory:
        if not Path(args.directory).exists():
            print(f"Error: Directory not found: {args.directory}")
            sys.exit(1)
        
        recursive = not args.no_recursive
        mode = "recursive" if recursive else "non-recursive"
        print(f"Scanning directory ({mode})...")
        
        rag.ingest_directory(args.directory, args.extensions, recursive=recursive)
        print(f"Successfully ingested directory: {args.directory}")
    
    elif args.text:
        rag.ingest_text(args.text, metadata={'source': 'command_line'})
        print("Successfully ingested text")
    
    # Save the updated vector store
    rag.save()
    
    # Show stats
    stats = rag.get_stats()
    print(f"\nTotal chunks in system: {stats['num_chunks']}")


def handle_query(rag: RAGEngine, args):
    """Handle query execution."""
    stats = rag.get_stats()
    if stats['num_chunks'] == 0:
        print("Error: No documents in the system. Please ingest documents first.")
        sys.exit(1)
    
    verbose = args.verbose if hasattr(args, 'verbose') else False
    
    # Determine save_results setting
    save_results = None
    if hasattr(args, 'save_results') and args.save_results:
        save_results = True
    elif hasattr(args, 'no_save_results') and args.no_save_results:
        save_results = False
    
    # Use retrieve with save_results parameter
    retrieved_docs = rag.retrieve(args.question, top_k=args.top_k, verbose=verbose, save_results=save_results)
    context = rag.get_context(args.question, top_k=args.top_k)
    
    result = {
        'question': args.question,
        'context': context,
        'retrieved_docs': retrieved_docs,
        'num_docs': len(retrieved_docs)
    }
    
    if args.context_only:
        print(result['context'])
    else:
        print(format_rag_response(result))


def handle_stats(rag: RAGEngine):
    """Handle statistics display."""
    stats = rag.get_stats()
    
    print("\n" + "=" * 80)
    print("RAG SYSTEM STATISTICS")
    print("=" * 80)
    print(f"Total chunks: {stats['num_chunks']}")
    print(f"Embedding dimension: {stats['dimension']}")
    print(f"Index size: {stats['index_size']}")
    print(f"\nSources ({len(stats['sources'])}):")
    for source in stats['sources']:
        print(f"  - {source}")
    print("=" * 80)


def handle_clear(rag: RAGEngine):
    """Handle vector store clearing."""
    confirm = input("Are you sure you want to clear the vector store? (yes/no): ")
    if confirm.lower() == 'yes':
        rag.clear()
        print("Vector store cleared successfully")
    else:
        print("Operation cancelled")


def handle_list_queries(rag: RAGEngine):
    """Handle listing saved query results."""
    if not rag.query_saver:
        print("Query result saving is not enabled. Set 'query_results.save_results: true' in config.yaml")
        return
    
    queries = rag.query_saver.list_saved_queries()
    
    if not queries:
        print("No saved query results found.")
        return
    
    print("\n" + "=" * 80)
    print("SAVED QUERY RESULTS")
    print("=" * 80)
    print(f"Total saved queries: {len(queries)}\n")
    
    for i, q in enumerate(queries, 1):
        timestamp = q.get('timestamp', 'Unknown')
        query_text = q.get('query', 'Unknown')
        raw_count = q.get('raw_result_count', 0)
        reranked_count = q.get('reranked_result_count', 0)
        folder = q.get('folder', '')
        
        print(f"{i}. [{timestamp}]")
        print(f"   Query: {query_text[:70]}{'...' if len(query_text) > 70 else ''}")
        print(f"   Results: {raw_count} raw, {reranked_count} reranked")
        print(f"   Folder: {folder}")
        print()
    
    print("=" * 80)
    print(f"\nTo load a query result: python main.py load-query <folder_name>")


def handle_load_query(rag: RAGEngine, args):
    """Handle loading saved query results."""
    if not rag.query_saver:
        print("Query result saving is not enabled. Set 'query_results.save_results: true' in config.yaml")
        return
    
    # Determine folder path
    import os
    folder_path = args.folder
    if not os.path.isabs(folder_path):
        # Relative path, assume it's in the query_results directory
        folder_path = os.path.join(rag.query_saver.output_dir, args.folder)
    
    if not os.path.exists(folder_path):
        print(f"Error: Query results folder not found: {folder_path}")
        return
    
    # Load results
    results = rag.query_saver.load_query_results(folder_path)
    
    if 'metadata' not in results:
        print(f"Error: Invalid query results folder (no metadata found)")
        return
    
    metadata = results['metadata']
    print("\n" + "=" * 80)
    print("LOADED QUERY RESULTS")
    print("=" * 80)
    print(f"Query: {metadata.get('query', 'Unknown')}")
    print(f"Timestamp: {metadata.get('timestamp', 'Unknown')}")
    print(f"Reranker used: {'Yes' if metadata.get('reranker_used', False) else 'No'}")
    print("=" * 80 + "\n")
    
    # Show raw results
    if 'raw' in results:
        raw_data = results['raw']
        print(f"Raw Retrieval Results ({raw_data.get('result_count', 0)} results):")
        print("-" * 80)
        for i, result in enumerate(raw_data.get('results', [])[:10], 1):  # Show top 10
            source = result.get('metadata', {}).get('source', 'Unknown')
            score = result.get('score', 0.0)
            print(f"{i}. Score: {score:.4f} | {os.path.basename(source)}")
            if args.show_content:
                content = result.get('content', '')[:200]
                print(f"   {content}...\n")
        print()
    
    # Show reranked results
    if 'reranked' in results:
        reranked_data = results['reranked']
        print(f"Reranked Results ({reranked_data.get('result_count', 0)} results):")
        print("-" * 80)
        for i, result in enumerate(reranked_data.get('results', []), 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            score = result.get('score', 0.0)
            rerank_score = result.get('rerank_score', 'N/A')
            original_rank = result.get('original_rank', '?')
            
            rerank_str = f"{rerank_score:.4f}" if isinstance(rerank_score, (int, float)) else str(rerank_score)
            rank_change = original_rank - i if isinstance(original_rank, int) else 0
            change_str = f"(+{rank_change})" if rank_change > 0 else f"({rank_change})" if rank_change < 0 else "(=)"
            
            print(f"{i}. {change_str} Rerank: {rerank_str} | Vector: {score:.4f} | {os.path.basename(source)}")
            if args.show_content:
                content = result.get('content', '')[:200]
                print(f"   {content}...\n")
        print()
    
    print("=" * 80)
    print(f"Results loaded from: {folder_path}")


def handle_interactive(rag: RAGEngine, args):
    """Handle interactive query mode."""
    stats = rag.get_stats()
    if stats['num_chunks'] == 0:
        print("Error: No documents in the system. Please ingest documents first.")
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("INTERACTIVE QUERY MODE")
    print("=" * 80)
    print(f"System loaded with {stats['num_chunks']} chunks")
    print("Type 'exit' or 'quit' to leave interactive mode")
    print("Type 'stats' to show system statistics")
    print("=" * 80 + "\n")
    
    while True:
        try:
            question = input("\nYour question: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['exit', 'quit']:
                print("Exiting interactive mode...")
                break
            
            if question.lower() == 'stats':
                handle_stats(rag)
                continue
            
            result = rag.query(question, top_k=args.top_k)
            print("\n" + format_rag_response(result))
            
        except KeyboardInterrupt:
            print("\n\nExiting interactive mode...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
