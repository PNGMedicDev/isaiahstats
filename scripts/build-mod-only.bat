@echo off
echo ========================================
echo IsaiahStats - Build Mod Only
echo ========================================
echo.

set BUILD_DIR=%~dp0..\build\mod
set MOD_DIR=%~dp0..\mod

if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

cd /d "%MOD_DIR%"

echo Building mod...
call gradlew.bat clean build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build successful!
    echo Copying JAR to build directory...
    copy /Y "build\libs\*.jar" "%BUILD_DIR%\"
    echo.
    echo Mod JAR location: %BUILD_DIR%
    echo.
) else (
    echo.
    echo Build failed!
    echo.
)

pause
