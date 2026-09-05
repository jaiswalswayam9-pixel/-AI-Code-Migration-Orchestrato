Write-Host "Setting up backend..."
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd ..
Write-Host "Setting up frontend..."
cd frontend
npm install
cd ..
Write-Host "Done. Run docker-compose up to start services."
