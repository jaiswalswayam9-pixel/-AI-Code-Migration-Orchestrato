@echo off
echo Starting AI Code Migration Orchestrator...
start "Backend (FastAPI)" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
start "Frontend (Vite)" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"
echo.
echo Applications launched:
echo - Frontend Dashboard: http://localhost:5173
echo - Backend API & Docs: http://localhost:8000/docs
echo.
