@echo off
echo ===============================================================
echo Starting StegoCyber Application (Backend + Frontend)
echo ===============================================================

:: 1. Start Backend API
start "StegoCyber Backend API" cmd /c "cd /d "%~dp0backend" && set "PYTHONPATH=." && venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

:: 2. Wait 2 seconds
timeout /t 2 /nobreak >nul

:: 3. Start Frontend Dev Server
start "StegoCyber Frontend" cmd /c "cd /d "%~dp0frontend" && set "PATH=C:\Program Files\nodejs;%PATH%" && "C:\Program Files\nodejs\npm.cmd" run dev"

:: 4. Wait 3 seconds and launch browser
timeout /t 3 /nobreak >nul
echo Opening StegoCyber in default browser...
start http://127.0.0.1:5173
