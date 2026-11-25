# EvidenceGraph AI One-Click PowerShell Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "      STARTING EVIDENCEGRAPH AI PLATFORM" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$env:PATH = "C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64;$env:PATH"

Write-Host "[*] Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\backend'; python app\main.py"

Write-Host "[*] Starting React Vite Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PATH = 'C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64;' + `$env:PATH; cd 'C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\frontend'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "[*] Opening browser at http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"

Write-Host "Application launched successfully!" -ForegroundColor Cyan
