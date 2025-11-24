@echo off
echo ========================================
echo IsaiahStats - Website Setup
echo ========================================
echo.

set WEBSITE_DIR=%~dp0..\website

cd /d "%WEBSITE_DIR%"

echo Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found! Please install Python 3.8 or later.
    pause
    exit /b 1
)

echo.
echo Installing dependencies...
echo.

pip install Flask==3.0.0
pip install Flask-SocketIO==5.3.5
pip install Flask-CORS==4.0.0
pip install python-socketio==5.10.0

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Setup complete!
    echo.
    echo To start the server, run: python app.py
    echo Or use: start-website.bat
    echo.
) else (
    echo.
    echo Setup failed! Please check the error messages above.
    echo.
)

pause
