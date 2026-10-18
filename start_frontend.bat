@echo off
echo ========================================================
echo Starting StegoCyber Frontend Server (Vite + React)
echo ========================================================
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "%~dp0frontend"
call npm run dev
pause
