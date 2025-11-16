@echo off
REM Setup script for Cryptocurrency MCP Server (Windows)

echo ========================================
echo Cryptocurrency MCP Server Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/5] Python found
python --version
echo.

REM Create virtual environment
echo [2/5] Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment and install dependencies
echo [3/5] Installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed
echo.

REM Create .env file if it doesn't exist
echo [4/5] Setting up environment configuration...
if exist .env (
    echo .env file already exists
) else (
    copy .env.example .env
    echo .env file created - PLEASE ADD YOUR API KEY!
)
echo.

REM Run tests to verify installation
echo [5/5] Running tests to verify installation...
pytest tests/ -v --tb=short
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env and add your CoinMarketCap API key
echo 2. Get a free API key from: https://coinmarketcap.com/api/
echo 3. Run the server: python -m src.server
echo 4. View examples: python examples\usage_examples.py
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate
echo.

pause
