@echo off
REM Fleet Forecasting Engine - Startup Script (Windows)
REM Developed by Irsandi Habibie

echo.
echo 🚛 Fleet Forecasting Engine
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo ✅ Setup complete!
echo.
echo 🚀 Starting Fleet Forecasting Engine...
echo 🌐 The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

REM Run the app
streamlit run app.py

pause
