#!/bin/bash
# Setup script for Cryptocurrency MCP Server (Linux/Mac)

echo "========================================"
echo "Cryptocurrency MCP Server Setup"
echo "========================================"
echo

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/5] Python found"
python3 --version
echo

# Create virtual environment
echo "[2/5] Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists"
else
    python3 -m venv venv
    echo "Virtual environment created"
fi
echo

# Activate virtual environment and install dependencies
echo "[3/5] Installing dependencies..."
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "Dependencies installed"
echo

# Create .env file if it doesn't exist
echo "[4/5] Setting up environment configuration..."
if [ -f ".env" ]; then
    echo ".env file already exists"
else
    cp .env.example .env
    echo ".env file created - PLEASE ADD YOUR API KEY!"
fi
echo

# Run tests to verify installation
echo "[5/5] Running tests to verify installation..."
pytest tests/ -v --tb=short
echo

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit .env and add your CoinMarketCap API key"
echo "2. Get a free API key from: https://coinmarketcap.com/api/"
echo "3. Run the server: python -m src.server"
echo "4. View examples: python examples/usage_examples.py"
echo
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo
