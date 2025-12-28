@echo off
chcp 65001 >nul
setlocal

echo === Performance Testing Setup ===
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Generating gRPC proto files...
cd grpc_app
python generate_proto.py
cd ..

echo.
echo Seeding databases...
python scripts\seed_database.py

echo.
echo === Setup Complete ===
echo.
echo To run tests:
echo.
echo 1. Start REST server (new terminal):
echo    cd rest_app ^&^& ..\venv\Scripts\uvicorn app.main:app --host 0.0.0.0 --port 8000
echo.
echo 2. Start gRPC server (new terminal):
echo    cd grpc_app ^&^& ..\venv\Scripts\python server.py
echo.
echo 3. Run Locust REST tests:
echo    venv\Scripts\locust -f locustfiles\rest_locustfile.py --host http://localhost:8000
echo.
echo 4. Run Locust gRPC tests:
echo    venv\Scripts\locust -f locustfiles\grpc_locustfile.py
echo.
echo Open http://localhost:8089 for Locust web UI
echo.

pause

