#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# Graceful cleanup on Ctrl+C / EXIT
trap 'echo "Shutting down all services..."; kill 0' EXIT INT TERM

echo "================================================="
echo " Starting CMS FastAPI Microservices"
echo "  - API Gateway : http://127.0.0.1:8080"
echo "  - User Service: http://127.0.0.1:8001"
echo "  - Auth Service: http://127.0.0.1:8002"
echo "  - Content Service: http://127.0.0.1:8003"
echo "================================================="

(cd api-gateway && uv run uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload) &
(cd user-service && uv run uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload) &
(cd auth-service && uv run uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload) &
(cd content-service && uv run uvicorn app.main:app --host 127.0.0.1 --port 8003 --reload)

wait
