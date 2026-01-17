@echo off
REM Test script for Qwen3-VL-Reranker endpoint (Windows)

set SERVER_URL=http://100.126.235.19:1111

echo ==========================================
echo Testing Qwen3-VL-Reranker Endpoints
echo ==========================================
echo.

REM Test 1: Check if /v1/rerank endpoint exists
echo Test 1: POST /v1/rerank (Native reranker endpoint)
echo --------------------------------------------------
curl -X POST "%SERVER_URL%/v1/rerank" ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"Qwen3-VL-Reranker-8B\", \"query\": \"What is machine learning?\", \"documents\": [\"Machine learning is a subset of AI.\", \"Python is a programming language.\", \"Coffee is a beverage.\"]}"
echo.
echo.

REM Test 2: Try /v1/completions endpoint with reranking prompt
echo Test 2: POST /v1/completions (Using completion for reranking)
echo --------------------------------------------------------------
curl -X POST "%SERVER_URL%/v1/completions" ^
  -H "Content-Type: application/json" ^
  -d "{\"prompt\": \"Query: What is machine learning?\\nDocument: Machine learning is a subset of AI that enables systems to learn from data.\\n\\nRate the relevance of the document to the query on a scale from 0 to 1:\\nRelevance score:\", \"temperature\": 0.0, \"max_tokens\": 10, \"stop\": [\"\\n\"]}"
echo.
echo.

REM Test 3: Try /v1/chat/completions endpoint
echo Test 3: POST /v1/chat/completions (Chat format for reranking)
echo --------------------------------------------------------------
curl -X POST "%SERVER_URL%/v1/chat/completions" ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"Qwen3-VL-Reranker-8B\", \"messages\": [{\"role\": \"system\", \"content\": \"You are a relevance scoring assistant. Rate document relevance to queries on a scale from 0 to 1.\"}, {\"role\": \"user\", \"content\": \"Query: What is machine learning?\\nDocument: Machine learning is a subset of AI.\\n\\nRelevance score (0-1):\"}], \"temperature\": 0.0, \"max_tokens\": 10}"
echo.
echo.

REM Test 4: Check models endpoint
echo Test 4: GET /v1/models (List available models)
echo ----------------------------------------------
curl -X GET "%SERVER_URL%/v1/models"
echo.
echo.

echo ==========================================
echo Tests Complete
echo ==========================================
pause
