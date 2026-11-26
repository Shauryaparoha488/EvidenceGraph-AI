@echo off
echo ===================================================
echo       STARTING EVIDENCEGRAPH AI PLATFORM
echo ===================================================

set "PYTHON_EXE=C:\Users\shaur\AppData\Local\Programs\Python\Python312\python.exe"
set "NODE_PATH=C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64"
set "PATH=%NODE_PATH%;%PATH%"

echo [*] Launching FastAPI Backend on http://localhost:8000 ...
start "EvidenceGraph Backend" cmd /k "cd /d C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\backend && "%PYTHON_EXE%" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [*] Launching React Vite Frontend on http://localhost:5173 ...
start "EvidenceGraph Frontend" cmd /k "set PATH=%NODE_PATH%;%%PATH%% && cd /d C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\frontend && npm run dev"

timeout /t 4 /nobreak >nul

echo [*] Opening EvidenceGraph AI in your browser...
start http://localhost:5173

echo ===================================================
echo EvidenceGraph AI is now running!
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo ===================================================
pause
