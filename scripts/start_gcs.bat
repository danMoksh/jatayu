@echo off
echo Starting Jatayu GCS Services...

start "Jatayu Backend" cmd /k "cd gcs\backend && call venv\Scripts\activate.bat && python run.py"
start "Jatayu Frontend" cmd /k "cd gcs\frontend && npm run dev"

echo Services launched in separate terminal windows.
