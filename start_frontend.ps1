$Host.UI.RawUI.WindowTitle = "StegoCyber Frontend"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Starting StegoCyber Frontend Server (Vite + React)" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
$env:PATH = "C:\Program Files\nodejs;" + $env:PATH
Set-Location "$PSScriptRoot\frontend"
& "C:\Program Files\nodejs\npm.cmd" run dev
