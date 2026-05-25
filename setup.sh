#!/bin/bash

# Quick Setup Script for Health Assistant on macOS/Linux

echo ""
echo "================================================"
echo "  AI Health Assistant - Quick Setup"
echo "================================================"
echo ""

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher from python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

echo ""
echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""

echo "Next steps:"
echo "1. Create a MySQL database:"
echo "   mysql> CREATE DATABASE health_assistant;"
echo ""
echo "2. Create .env file from .env.example and update database credentials"
echo ""
echo "3. Initialize the database:"
echo "   python -c \"from config.db_config import initialize_database; initialize_database()\""
echo ""
echo "4. Run the application:"
echo "   python app.py"
echo ""
echo "The app will be available at: http://localhost:5000"
echo ""
