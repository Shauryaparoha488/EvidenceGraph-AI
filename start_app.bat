@echo off
echo ===================================================
echo       STARTING EVIDENCEGRAPH AI PLATFORM
echo ===================================================

set "PATH=C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64;%PATH%"

echo [*] Launching FastAPI Backend on http://localhost:8000 ...
start "EvidenceGraph Backend" cmd /k "cd /d C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\backend && python app\main.py"

echo [*] Launching React Vite Frontend on http://localhost:5173 ...
start "EvidenceGraph Frontend" cmd /k "set PATH=C:\Users\shaur\OneDrive\Documents\node-v20.18.1-win-x64;%%PATH%% && cd /d C:\Users\shaur\OneDrive\Documents\EvidenceGraph-AI\frontend && npm run dev"

timeout /t 3 /nobreak >nul

echo [*] Opening EvidenceGraph AI in your browser...
start http://localhost:5173

echo ===================================================
echo EvidenceGraph AI is now running!
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000/docs
echo ===================================================
pause
