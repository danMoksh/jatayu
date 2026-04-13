@echo off
echo ==================================================
echo   Jatayu VTOL - Windows Setup
echo ==================================================

echo [1/2] Installing Backend Dependencies...
cd gcs\backend
python -m venv venv
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
cd ..\..

echo [2/2] Installing Frontend Dependencies...
cd gcs\frontend
call npm install
cd ..\..

echo Setup complete. Run scripts\start_gcs.bat to launch.
pause
