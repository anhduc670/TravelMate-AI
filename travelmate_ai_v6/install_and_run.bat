@echo off
cd /d "%~dp0"
echo Dang cai thu vien giao dien...
python -m pip install -r requirements.txt
echo.
echo Dang khoi dong TravelMate AI v6...
python app.py
pause
