@echo off
REM RAG System Launcher for Windows Command Prompt

setlocal enabledelayedexpansion

echo ============================================
echo Qwen3VL RAG System
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating...
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import faiss" 2>nul
if errorlevel 1 (
    echo Dependencies not installed. Installing...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        echo Please check the error messages above
        goto :end
    )
    echo [OK] Dependencies installed
)

echo [OK] Environment ready
echo.

REM Run the application
if "%1"=="" (
    echo Usage: run.bat [command] [options]
    echo.
    echo Commands:
    echo   interactive               - Start interactive mode
    echo   ingest ^<path^>             - Ingest documents from path
    echo                                 (PDFs processed with Granite VLM)
    echo   query "question"          - Query the system
    echo   query "question" -v       - Query with verbose reranker output
    echo   stats                     - Show statistics
    echo   clear                     - Clear the vector store
    echo   help                      - Show full help
    echo.
    echo Examples:
    echo   run.bat interactive
    echo   run.bat ingest .\sample_docs
    echo   run.bat ingest "C:\Documents\Reports"
    echo   run.bat query "What is Python?"
    echo   run.bat query "Explain RAG" -v
    echo.
    goto :end
)

if "%1"=="interactive" (
    python main.py interactive
    goto :end
)

if "%1"=="ingest" (
    if "%~2"=="" (
        echo [ERROR] Please specify a path to ingest
        echo Usage: run.bat ingest ^<path^>
        echo Note: Use double quotes for paths with spaces
        goto :end
    )
    REM Remove quotes from the path and check if it exists
    set "INGEST_PATH=%~2"
    
    if exist "!INGEST_PATH!\*" (
        python main.py ingest --directory "!INGEST_PATH!"
    ) else if exist "!INGEST_PATH!" (
        python main.py ingest --file "!INGEST_PATH!"
    ) else (
        echo [ERROR] Path not found: !INGEST_PATH!
        echo Make sure the path exists and use double quotes for paths with spaces
        goto :end
    )
    goto :end
)

if "%1"=="query" (
    if "%~2"=="" (
        echo [ERROR] Please provide a question
        echo Usage: run.bat query "your question" [-v or --verbose]
        goto :end
    )
    REM Strip and re-quote the query string
    set "QUERY_TEXT=%~2"
    set "EXTRA_ARGS="
    
    REM Check for verbose flag
    if "%~3"=="-v" set "EXTRA_ARGS=--verbose"
    if "%~3"=="--verbose" set "EXTRA_ARGS=--verbose"
    
    python main.py query "!QUERY_TEXT!" !EXTRA_ARGS!
    goto :end
)

if "%1"=="stats" (
    python main.py stats
    goto :end
)

if "%1"=="clear" (
    python main.py clear
    goto :end
)

if "%1"=="help" (
    python main.py --help
    goto :end
)

REM Pass all arguments to main.py
python main.py %*

:end
endlocal
