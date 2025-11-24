@echo off
echo ========================================
echo IsaiahStats - Build All
echo ========================================
echo.

REM Set build directory
set BUILD_DIR=%~dp0..\build
set MOD_DIR=%~dp0..\mod
set WEBSITE_DIR=%~dp0..\website

echo Cleaning build directory...
if exist "%BUILD_DIR%" rmdir /s /q "%BUILD_DIR%"
mkdir "%BUILD_DIR%"
mkdir "%BUILD_DIR%\website"
mkdir "%BUILD_DIR%\mod"

echo.
echo ========================================
echo Building Minecraft Mod...
echo ========================================
cd /d "%MOD_DIR%"

REM Check if gradlew exists
if not exist "gradlew.bat" (
    echo ERROR: gradlew.bat not found. Please run gradle wrapper first.
    echo Running: gradle wrapper
    call gradle wrapper
)

REM Build the mod
echo Building mod with Gradle...
call gradlew.bat clean build

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Mod build failed!
    pause
    exit /b 1
)

echo Copying mod JAR to build directory...
copy /Y "build\libs\*.jar" "%BUILD_DIR%\mod\"

echo.
echo ========================================
echo Preparing Website Files...
echo ========================================
cd /d "%WEBSITE_DIR%"

echo Copying website files...
xcopy /E /I /Y "static" "%BUILD_DIR%\website\static"
xcopy /E /I /Y "templates" "%BUILD_DIR%\website\templates"
copy /Y "app.py" "%BUILD_DIR%\website\"

echo Creating requirements.txt...
(
    echo Flask==3.0.0
    echo Flask-SocketIO==5.3.5
    echo Flask-CORS==4.0.0
    echo python-socketio==5.10.0
) > "%BUILD_DIR%\website\requirements.txt"

echo Creating website start script...
(
    echo @echo off
    echo echo Starting IsaiahStats Website...
    echo echo.
    echo echo Visit http://localhost:5000
    echo echo.
    echo python app.py
    echo pause
) > "%BUILD_DIR%\website\start-server.bat"

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo.
echo Mod JAR: %BUILD_DIR%\mod\
echo Website: %BUILD_DIR%\website\
echo.
echo To start the website:
echo 1. cd build\website
echo 2. pip install -r requirements.txt
echo 3. run start-server.bat
echo.
echo To install the mod:
echo 1. Copy the JAR from build\mod\ to your .minecraft\mods folder
echo 2. Make sure you have Fabric Loader installed for Minecraft 1.21.3
echo.
pause
