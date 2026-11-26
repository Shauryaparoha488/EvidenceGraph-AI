# EvidenceGraph AI One-Click PowerShell Launcher
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "      STARTING EVIDENCEGRAPH AI PLATFORM" -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

$pythonExe = "C:\Users\shaur\AppData\Local\Programs\Python\Python312\python.exe"
$nodePath = "C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64"
$env:PATH = "$nodePath;$env:PATH"

Write-Host "[*] Starting FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\backend'; & '$pythonExe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[*] Starting React Vite Frontend on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:PATH = '$nodePath;' + `$env:PATH; cd 'C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\frontend'; npm run dev"

Start-Sleep -Seconds 4

Write-Host "[*] Opening browser at http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process "http://localhost:5173"

Write-Host "Application launched successfully!" -ForegroundColor Cyan
