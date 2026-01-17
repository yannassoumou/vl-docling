# Setup Milvus with Docker for Windows PowerShell

function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }
function Write-Info { Write-Host $args -ForegroundColor Cyan }

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Milvus Setup for RAG System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Error "Error: Docker is not installed"
    Write-Host "Please install Docker Desktop for Windows:"
    Write-Host "https://docs.docker.com/desktop/install/windows-install/"
    exit 1
}

# Check if Docker Compose is installed
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
} catch {
    Write-Error "Error: Docker Compose is not installed"
    Write-Host "Please install Docker Compose"
    exit 1
}

Write-Success "✓ Docker and Docker Compose are installed"
Write-Host ""

# Check if Milvus is already running
$running = docker-compose ps 2>$null | Select-String "milvus-standalone"
if ($running) {
    Write-Warning "Milvus is already running"
    Write-Host ""
    $restart = Read-Host "Do you want to restart it? (y/n)"
    if ($restart -eq 'y' -or $restart -eq 'Y') {
        Write-Host "Stopping Milvus..."
        docker-compose down
    } else {
        Write-Host "Keeping current Milvus instance"
        exit 0
    }
}

# Start Milvus
Write-Host "Starting Milvus..."
docker-compose up -d

Write-Host ""
Write-Host "Waiting for Milvus to start (this may take 30-60 seconds)..."
Start-Sleep -Seconds 10

# Check if Milvus is running
$maxAttempts = 12
$attempt = 0
$success = $false

while ($attempt -lt $maxAttempts) {
    $status = docker-compose ps 2>$null | Select-String "milvus-standalone.*Up"
    if ($status) {
        Write-Success "✓ Milvus is running"
        $success = $true
        break
    }
    
    $attempt++
    if ($attempt -eq $maxAttempts) {
        Write-Error "Error: Milvus failed to start"
        Write-Host "Check logs with: docker-compose logs"
        exit 1
    }
    
    Write-Host "Still waiting... ($attempt/$maxAttempts)"
    Start-Sleep -Seconds 5
}

if ($success) {
    Write-Host ""
    Write-Success "✓ Milvus setup complete!"
    Write-Host ""
    Write-Info "Milvus is running at: localhost:19530"
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Configure the RAG system:"
    Write-Host "     `"VECTOR_STORE_TYPE=milvus`" | Out-File .env -Encoding ASCII"
    Write-Host ""
    Write-Host "  2. Test with example:"
    Write-Host "     .\run.ps1 example-milvus"
    Write-Host ""
    Write-Host "  3. Use in your application:"
    Write-Host "     .\run.ps1 ingest .\sample_docs"
    Write-Host "     .\run.ps1 query `"What is Python?`""
    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  - Stop Milvus: docker-compose down"
    Write-Host "  - View logs: docker-compose logs -f"
    Write-Host "  - Check status: docker-compose ps"
}
