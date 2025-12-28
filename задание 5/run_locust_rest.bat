@echo off
chcp 65001 >nul
call venv\Scripts\activate.bat
echo Starting Locust for REST tests...
echo Open http://localhost:8089
locust -f locustfiles\rest_locustfile.py --host http://localhost:8000

