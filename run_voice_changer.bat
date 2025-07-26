@echo off
:: Dark Helmet Voice Changer Launcher for Windows
:: Activates SpaceBalls environment and runs the voice changer

title Dark Helmet Voice Changer - SpaceBalls Edition

echo.
echo ==========================================
echo  🎭 Dark Helmet Voice Changer Launcher
echo ==========================================
echo.

:: Check if we're in the right directory
if not exist "SpaceBalls" (
    echo ❌ SpaceBalls virtual environment not found!
    echo Please run this script from the project root directory.
    echo.
    echo To set up the environment:
    echo   cd scripts
    echo   python setup_venv.py
    echo.
    pause
    exit /b 1
)

:: Activate SpaceBalls environment
echo 🚀 Activating SpaceBalls virtual environment...
call SpaceBalls\Scripts\activate.bat

:: Change to src directory
cd src

:: Check if required files exist
if not exist "voice_changer.py" (
    echo ❌ voice_changer.py not found in src directory!
    pause
    exit /b 1
)

if not exist "index.html" (
    echo ❌ index.html not found in src directory!
    pause
    exit /b 1
)

echo ✅ SpaceBalls environment active!
echo 🎤 Starting Dark Helmet Voice Changer...
echo.
echo 🌐 Web interface will be available at:
echo    http://localhost:8000
echo.
echo 🛑 Press Ctrl+C to stop the voice changer
echo ==========================================
echo.

:: Run the voice changer
python run_voice_changer.py

echo.
echo 🎭 Voice changer stopped. May the Schwartz be with you!
pause
