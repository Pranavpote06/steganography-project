@echo off
echo ============================================
echo Starting StegoCyber Application
echo ============================================
echo.

echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo Found process %%a on port 8000, killing it...
    taskkill /F /PID %%a >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo Starting Backend Server on port 8000...
cd backend
start "StegoCyber Backend" cmd /k "python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
cd ..\frontend
start "StegoCyber Frontend" cmd /k "npm run dev"

timeout /t 3 /nobreak >nul

echo.
echo ============================================
echo Servers Starting!
echo ============================================
echo.
echo Frontend will be available at:
echo   http://localhost:5173
echo   (or http://localhost:5174 if 5173 is in use)
echo   (or http://localhost:5175 if 5174 is in use)
echo.
echo Backend API:
echo   http://localhost:8000
echo.
echo Wait 10 seconds for servers to fully start...
echo Then open the frontend URL in your browser!
echo.
echo Press any key to exit this window...
pause >nul
