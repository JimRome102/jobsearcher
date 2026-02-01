#!/bin/bash

clear
echo "=========================================="
echo "  Job Search Assistant - Easy Setup"
echo "=========================================="
echo ""
echo "I'll do most of the work. You just need to:"
echo "1. Get a Gmail OAuth file (I'll show you)"
echo "2. Get an AI API key (I'll show you)"
echo ""
read -p "Ready? Press Enter..."

# Install dependencies
echo ""
echo "Installing dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Create directories
mkdir -p data config

# Create .env file
if [ ! -f .env ]; then
    cp .env.example .env
fi

# Initialize database
echo "Setting up database..."
python3 -c "from src.database import db; db.create_tables()" 2>/dev/null

clear
echo "=========================================="
echo "  STEP 1: Gmail Setup"
echo "=========================================="
echo ""
echo "I need you to do this once (3 minutes):"
echo ""
echo "1. Go to this URL (Cmd+Click to open):"
echo "   https://console.cloud.google.com/projectcreate"
echo ""
echo "   - Project name: JobSearch"
echo "   - Click 'Create'"
echo ""
read -p "Done? Press Enter..."

echo ""
echo "2. Go to this URL:"
echo "   https://console.cloud.google.com/apis/library/gmail.googleapis.com"
echo ""
echo "   - Click 'Enable'"
echo ""
read -p "Done? Press Enter..."

echo ""
echo "3. Go to this URL:"
echo "   https://console.cloud.google.com/apis/credentials/oauthclient"
echo ""
echo "   - Click 'Configure Consent Screen'"
echo "   - Choose 'External' → 'Create'"
echo "   - App name: JobSearch"
echo "   - Your email: romejim@gmail.com"
echo "   - Developer email: romejim@gmail.com"
echo "   - Click 'Save and Continue' 3 times"
echo "   - Click 'Back to Dashboard'"
echo ""
read -p "Done? Press Enter..."

echo ""
echo "4. Go to this URL:"
echo "   https://console.cloud.google.com/apis/credentials/oauthclient"
echo ""
echo "   - Application type: 'Desktop app'"
echo "   - Name: JobSearch"
echo "   - Click 'Create'"
echo "   - Click 'Download JSON'"
echo ""
read -p "Downloaded? Press Enter..."

echo ""
echo "5. Move the file you just downloaded:"
echo ""
echo "Drag the file from Downloads to Finder, or run this:"
echo "mv ~/Downloads/client_secret_*.json config/gmail_credentials.json"
echo ""
read -p "Moved the file? Press Enter..."

# Check if file exists
while [ ! -f config/gmail_credentials.json ]; do
    echo ""
    echo "❌ File not found at config/gmail_credentials.json"
    echo ""
    echo "Please move the downloaded file:"
    echo "mv ~/Downloads/client_secret_*.json config/gmail_credentials.json"
    echo ""
    read -p "Try again? Press Enter..."
done

echo ""
echo "✅ Gmail credentials found!"

clear
echo "=========================================="
echo "  STEP 2: AI API Key"
echo "=========================================="
echo ""
echo "1. Go to this URL (Cmd+Click to open):"
echo "   https://console.anthropic.com/settings/keys"
echo ""
echo "   - Click 'Create Key'"
echo "   - Copy the key (starts with sk-ant-)"
echo ""
read -p "Got your API key? Press Enter..."

echo ""
echo "2. Paste your API key:"
read -p "ANTHROPIC_API_KEY: " api_key

# Add to .env
if grep -q "ANTHROPIC_API_KEY=" .env; then
    # Replace existing
    sed -i.bak "s/ANTHROPIC_API_KEY=.*/ANTHROPIC_API_KEY=$api_key/" .env
else
    # Add new
    echo "ANTHROPIC_API_KEY=$api_key" >> .env
fi

# Add email to .env
if ! grep -q "USER_EMAIL=" .env; then
    echo "USER_EMAIL=romejim@gmail.com" >> .env
fi

echo ""
echo "✅ API key saved!"

clear
echo "=========================================="
echo "  STEP 3: Authorize Gmail"
echo "=========================================="
echo ""
echo "A browser will open. Just click 'Allow'."
echo ""
read -p "Ready? Press Enter..."

# Run OAuth flow
python3 setup_gmail_oauth.py

clear
echo "=========================================="
echo "  ✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Test it now:"
echo "  python src/main.py search"
echo ""
echo "Start 2x daily automation:"
echo "  python src/scheduler.py"
echo ""
echo "Check your email at romejim@gmail.com"
echo ""
