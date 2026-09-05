#!/bin/bash
set -e
echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd ..
echo "Setting up frontend..."
cd frontend
npm install
cd ..
echo "Done. Run docker-compose up to start services."
