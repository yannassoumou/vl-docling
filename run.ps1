# RAG System Launcher for Windows PowerShell

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Qwen3VL RAG System" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Warning "Virtual environment not found. Creating..."
    python -m venv .venv
    Write-Success "[OK] Virtual environment created"
}

# Activate virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Check if dependencies are installed
$faissInstalled = python -c "import faiss" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Dependencies not installed. Installing..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "[FAIL] Failed to install dependencies"
        Write-Host "Please check the error messages above"
        exit 1
    }
    Write-Success "[OK] Dependencies installed"
}

Write-Success "[OK] Environment ready"
Write-Host ""

# Function to show usage
function Show-Usage {
    Write-Host "Usage: .\run.ps1 [command] [options]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  interactive               - Start interactive mode"
    Write-Host "  ingest PATH               - Ingest documents from path"
    Write-Host "                              (PDFs processed with Granite VLM)"
    Write-Host "  query QUESTION            - Query the system"
    Write-Host "  query QUESTION -v         - Query with verbose reranker output"
    Write-Host "  stats                     - Show statistics"
    Write-Host "  clear                     - Clear the vector store"
    Write-Host "  help                      - Show full help"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run.ps1 interactive"
    Write-Host "  .\run.ps1 ingest .\sample_docs"
    Write-Host "  .\run.ps1 ingest 'C:\Documents\Reports'"
    Write-Host "  .\run.ps1 query 'What is Python?'"
    Write-Host "  .\run.ps1 query 'Explain RAG' -v"
}

# Run the application
if (-not $Command) {
    Show-Usage
    exit 0
}

switch ($Command.ToLower()) {
    "interactive" {
        python main.py interactive
    }
    "ingest" {
        if (-not $Arguments) {
            Write-Error "Error: Please specify a path to ingest"
            Write-Host "Usage: .\run.ps1 ingest PATH"
            exit 1
        }
        $path = $Arguments[0]
        
        if (Test-Path $path -PathType Container) {
            python main.py ingest --directory $path
        }
        elseif (Test-Path $path -PathType Leaf) {
            python main.py ingest --file $path
        }
        else {
            Write-Error "Error: Path not found: $path"
            exit 1
        }
    }
    "query" {
        if (-not $Arguments) {
            Write-Error "Error: Please provide a question"
            Write-Host "Usage: .\run.ps1 query 'your question' [-v]"
            exit 1
        }
        # Check for verbose flag
        $verboseFlag = ""
        if ($Arguments -contains "-v" -or $Arguments -contains "--verbose") {
            $verboseFlag = "--verbose"
            $Arguments = $Arguments | Where-Object { $_ -ne "-v" -and $_ -ne "--verbose" }
        }
        $question = $Arguments -join " "
        if ($verboseFlag) {
            python main.py query $question $verboseFlag
        } else {
            python main.py query $question
        }
    }
    "stats" {
        python main.py stats
    }
    "clear" {
        python main.py clear
    }
    "help" {
        python main.py --help
    }
    default {
        # Pass all arguments to main.py
        python main.py $Command $Arguments
    }
}
