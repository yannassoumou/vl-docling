#!/bin/bash
# Setup Milvus with Docker for Linux/Mac

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================"
echo "Milvus Setup for RAG System"
echo "============================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker first:"
    echo "  - Linux: https://docs.docker.com/engine/install/"
    echo "  - Mac: https://docs.docker.com/desktop/install/mac-install/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose first:"
    echo "  https://docs.docker.com/compose/install/"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"
echo ""

# Check if Milvus is already running
if docker-compose ps | grep -q "milvus-standalone"; then
    echo -e "${YELLOW}Milvus is already running${NC}"
    echo ""
    read -p "Do you want to restart it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Stopping Milvus..."
        docker-compose down
    else
        echo "Keeping current Milvus instance"
        exit 0
    fi
fi

# Start Milvus
echo "Starting Milvus..."
docker-compose up -d

echo ""
echo "Waiting for Milvus to start (this may take 30-60 seconds)..."
sleep 10

# Check if Milvus is running
MAX_ATTEMPTS=12
ATTEMPT=0
while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    if docker-compose ps | grep -q "milvus-standalone.*Up"; then
        echo -e "${GREEN}✓ Milvus is running${NC}"
        break
    fi
    ATTEMPT=$((ATTEMPT + 1))
    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo -e "${RED}Error: Milvus failed to start${NC}"
        echo "Check logs with: docker-compose logs"
        exit 1
    fi
    echo "Still waiting... ($ATTEMPT/$MAX_ATTEMPTS)"
    sleep 5
done

echo ""
echo -e "${GREEN}✓ Milvus setup complete!${NC}"
echo ""
echo "Milvus is running at: localhost:19530"
echo ""
echo "Next steps:"
echo "  1. Configure the RAG system:"
echo "     echo 'VECTOR_STORE_TYPE=milvus' > .env"
echo ""
echo "  2. Test with example:"
echo "     ./run.sh example-milvus"
echo ""
echo "  3. Use in your application:"
echo "     ./run.sh ingest ./sample_docs"
echo "     ./run.sh query \"What is Python?\""
echo ""
echo "Useful commands:"
echo "  - Stop Milvus: docker-compose down"
echo "  - View logs: docker-compose logs -f"
echo "  - Check status: docker-compose ps"
