@echo off
REM Quick Setup Script for Health Assistant on Windows

echo.
echo ================================================
echo  AI Health Assistant - Quick Setup (Windows)
echo ================================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo ================================================
echo  Setup Complete!
echo ================================================
echo.

echo Next steps:
echo 1. Create a MySQL database:
echo    mysql> CREATE DATABASE health_assistant;
echo.
echo 2. Create .env file from .env.example and update database credentials
echo.
echo 3. Initialize the database:
echo    python -c "from config.db_config import initialize_database; initialize_database()"
echo.
echo 4. Run the application:
echo    python app.py
echo.
echo The app will be available at: http://localhost:5000
echo.

pause
