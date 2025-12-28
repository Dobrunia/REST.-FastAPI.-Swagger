@echo off
chcp 65001 >nul
call venv\Scripts\activate.bat
cd grpc_app
echo Starting gRPC server on port 50051...
python server.py

