@echo off
REM Setup Milvus with Docker for Windows Command Prompt

setlocal enabledelayedexpansion

echo ============================================
echo Milvus Setup for RAG System
echo ============================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed
    echo Please install Docker Desktop for Windows:
    echo https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed
    echo Please install Docker Compose
    exit /b 1
)

echo [OK] Docker and Docker Compose are installed
echo.

REM Check if Milvus is already running
docker-compose ps | find "milvus-standalone" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Milvus is already running
    echo.
    set /p RESTART="Do you want to restart it? (y/n): "
    if /i "!RESTART!"=="y" (
        echo Stopping Milvus...
        docker-compose down
    ) else (
        echo Keeping current Milvus instance
        exit /b 0
    )
)

REM Start Milvus
echo Starting Milvus...
docker-compose up -d

echo.
echo Waiting for Milvus to start (this may take 30-60 seconds)...
timeout /t 10 /nobreak >nul

REM Check if Milvus is running
set ATTEMPT=0
set MAX_ATTEMPTS=12

:check_loop
docker-compose ps | find "milvus-standalone" | find "Up" >nul 2>&1
if not errorlevel 1 (
    echo [OK] Milvus is running
    goto :success
)

set /a ATTEMPT+=1
if !ATTEMPT! geq !MAX_ATTEMPTS! (
    echo [ERROR] Milvus failed to start
    echo Check logs with: docker-compose logs
    exit /b 1
)

echo Still waiting... (!ATTEMPT!/!MAX_ATTEMPTS!)
timeout /t 5 /nobreak >nul
goto :check_loop

:success
echo.
echo [OK] Milvus setup complete!
echo.
echo Milvus is running at: localhost:19530
echo.
echo Next steps:
echo   1. Configure the RAG system:
echo      echo VECTOR_STORE_TYPE=milvus ^> .env
echo.
echo   2. Test with example:
echo      run.bat example-milvus
echo.
echo   3. Use in your application:
echo      run.bat ingest .\sample_docs
echo      run.bat query "What is Python?"
echo.
echo Useful commands:
echo   - Stop Milvus: docker-compose down
echo   - View logs: docker-compose logs
echo   - Check status: docker-compose ps

endlocal
