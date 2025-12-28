@echo off
chcp 65001 >nul
call venv\Scripts\activate.bat
cd rest_app
echo Starting REST server on port 8000...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

