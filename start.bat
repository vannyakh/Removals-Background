@echo off
echo ================================================
echo 🎨 Background Removal Tool - Setup ^& Start
echo ================================================
echo.

REM Check if virtual environment exists
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM Create models directory
if not exist "service\models" mkdir service\models

REM Check if model exists
if not exist "service\models\u2net.pth" (
    echo.
    echo ⚠️  Model weights not found!
    echo 📥 Downloading U²-Net model (~176 MB^)...
    echo.
    python service\download_model.py
    echo.
)

REM Start the server
echo.
echo ================================================
echo 🚀 Starting Backend Server...
echo ================================================
echo.
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo 📝 To use the application:
echo    1. Open client\index.html in your browser
echo    OR
echo    2. Run: cd client ^&^& python -m http.server 3000
echo       Then visit: http://localhost:3000
echo.
echo Press CTRL+C to stop
echo ================================================
echo.

python main.py

