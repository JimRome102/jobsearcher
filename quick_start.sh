#!/bin/bash

# Quick Start Script for Job Search Assistant

echo "======================================"
echo "Job Search Assistant - Quick Start"
echo "======================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env file and add your API keys!"
    echo "    Run: nano .env"
fi

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from src.database import db; db.create_tables()"

echo ""
echo "======================================"
echo "✓ Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Set up Gmail OAuth2 (secure, no passwords!):"
echo "   python setup_gmail_oauth.py"
echo ""
echo "2. Edit .env file and add your AI API key:"
echo "   nano .env"
echo "   (Add: ANTHROPIC_API_KEY=sk-ant-xxxxx)"
echo ""
echo "3. Test the system:"
echo "   python src/main.py search"
echo ""
echo "4. Start the scheduler (runs 2x daily):"
echo "   python src/scheduler.py"
echo ""
echo "For more info, see README.md or GMAIL_OAUTH_SETUP.md"
echo ""
