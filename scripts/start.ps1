Write-Host 'Starting AI Code Migration Orchestrator...' -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd backend; python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000'
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd frontend; npm run dev -- --host 127.0.0.1 --port 5173'
Write-Host 'Services launched:' -ForegroundColor Green
Write-Host '  Frontend UI: http://localhost:5173' -ForegroundColor Yellow
Write-Host '  Backend Docs: http://localhost:8000/docs' -ForegroundColor Yellow
