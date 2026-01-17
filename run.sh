#!/bin/bash
# RAG System Launcher for Linux/Mac

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "Qwen3VL RAG System"
echo "============================================"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Check if dependencies are installed
if ! python -c "import faiss" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing...${NC}"
    if ! pip install -r requirements.txt; then
        echo -e "${RED}✗ Failed to install dependencies${NC}"
        echo "Please check the error messages above"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependencies installed${NC}"
fi

echo -e "${GREEN}✓ Environment ready${NC}"
echo ""

# Run the application
if [ "$1" == "" ]; then
    echo "Usage: ./run.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  interactive               - Start interactive mode"
    echo "  ingest <path>             - Ingest documents from path"
    echo "                              (PDFs processed with Granite VLM)"
    echo "  query \"question\"          - Query the system"
    echo "  query \"question\" -v       - Query with verbose reranker output"
    echo "  stats                     - Show statistics"
    echo "  clear                     - Clear the vector store"
    echo "  help                      - Show full help"
    echo ""
    echo "Examples:"
    echo "  ./run.sh interactive"
    echo "  ./run.sh ingest ./sample_docs"
    echo "  ./run.sh ingest /path/to/documents"
    echo "  ./run.sh query \"What is Python?\""
    echo "  ./run.sh query \"Explain RAG\" -v"
    echo ""
    exit 0
fi

case "$1" in
    interactive)
        python main.py interactive
        ;;
    ingest)
        if [ "$2" == "" ]; then
            echo -e "${RED}Error: Please specify a path to ingest${NC}"
            echo "Usage: ./run.sh ingest <path>"
            exit 1
        fi
        
        if [ -d "$2" ]; then
            python main.py ingest --directory "$2"
        elif [ -f "$2" ]; then
            python main.py ingest --file "$2"
        else
            echo -e "${RED}Error: Path not found: $2${NC}"
            exit 1
        fi
        ;;
    query)
        if [ "$2" == "" ]; then
            echo -e "${RED}Error: Please provide a question${NC}"
            echo "Usage: ./run.sh query \"your question\" [-v or --verbose]"
            exit 1
        fi
        # Check for verbose flag
        if [ "$3" == "-v" ] || [ "$3" == "--verbose" ]; then
            python main.py query "$2" --verbose
        else
            python main.py query "$2"
        fi
        ;;
    stats)
        python main.py stats
        ;;
    clear)
        python main.py clear
        ;;
    help)
        python main.py --help
        ;;
    *)
        python main.py "$@"
        ;;
esac
