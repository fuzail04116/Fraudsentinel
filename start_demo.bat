@echo off
echo Starting FraudSentinel MLOps Dashboard...

echo Starting FastAPI Backend on Port 8000...
start "FastAPI Backend" cmd /c ".\venv\Scripts\activate && uvicorn src.serving.main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting React Dashboard on Port 3000...
start "React Dashboard" cmd /c "cd dashboard && npm run dev"

echo Starting Real-Time Data Simulator...
start "Data Simulator" cmd /c ".\venv\Scripts\activate && python src\ingestion\run_demo.py"

echo.
echo All services are starting up!
echo Your dashboard will be available at: http://localhost:3000
echo.
pause
