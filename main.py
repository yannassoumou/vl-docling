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
    
    # Stats command
    subparsers.add_parser('stats', help='Show statistics about the RAG system')
    
    # Clear command
    subparsers.add_parser('clear', help='Clear the vector store')
    
    # Interactive command
    interactive_parser = subparsers.add_parser('interactive', help='Start interactive query mode')
    interactive_parser.add_argument('--top-k', type=int, default=5, help='Number of documents to retrieve')
    
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
    result = rag.query(args.question, top_k=args.top_k, verbose=verbose)
    
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
