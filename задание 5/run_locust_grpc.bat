@echo off
chcp 65001 >nul
call venv\Scripts\activate.bat
echo Starting Locust for gRPC tests...
echo Open http://localhost:8089
locust -f locustfiles\grpc_locustfile.py

