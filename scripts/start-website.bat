@echo off
echo ========================================
echo IsaiahStats - Starting Website
echo ========================================
echo.
echo Visit: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

cd /d "%~dp0..\website"
python app.py

pause
