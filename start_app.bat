@echo off
echo Starting ARMS Workflow System...

echo Stopping existing Python and Node processes...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM node.exe /T 2>nul

echo Starting Backend...
start "ARMS Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --port 8000"

echo Starting Frontend...
start "ARMS Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===================================================
echo   ARMS Workflow System Started
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo ===================================================
pause
