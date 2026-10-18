$Host.UI.RawUI.WindowTitle = "StegoCyber Backend API"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting StegoCyber Backend API Server (FastAPI)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
Set-Location "$PSScriptRoot\backend"
& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
