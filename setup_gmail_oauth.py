#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Script

This script helps you set up OAuth2 authentication for Gmail API.
It will guide you through creating credentials in Google Cloud Console
and testing the email functionality.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")


def print_step(number, text):
    """Print a formatted step."""
    print(f"\n📋 STEP {number}: {text}")
    print("-" * 70)


def main():
    """Main setup flow."""
    print_header("Gmail OAuth2 Setup for Job Search Assistant")

    print("""
This script will help you set up secure OAuth2 authentication for Gmail.

OAuth2 is more secure than app passwords because:
✅ No passwords stored anywhere
✅ Granular permissions (only send email)
✅ Can be revoked anytime from Google Account
✅ Tokens auto-refresh
✅ Industry-standard security

Let's get started!
""")

    input("Press Enter to continue...")

    # Step 1: Google Cloud Console
    print_step(1, "Create a Google Cloud Project")
    print("""
1. Go to: https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it: "Job Search Assistant"
4. Click "Create"
5. Wait for project creation to complete
""")
    input("✓ Done? Press Enter to continue...")

    # Step 2: Enable Gmail API
    print_step(2, "Enable Gmail API")
    print("""
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Gmail API"
3. Click on "Gmail API"
4. Click "Enable"
5. Wait for API to be enabled
""")
    input("✓ Done? Press Enter to continue...")

    # Step 3: Configure OAuth Consent Screen
    print_step(3, "Configure OAuth Consent Screen")
    print("""
1. Go to: https://console.cloud.google.com/apis/credentials/consent
2. Select "External" user type
3. Click "Create"

4. Fill in the form:
   - App name: Job Search Assistant
   - User support email: romejim@gmail.com
   - Developer contact: romejim@gmail.com

5. Click "Save and Continue"

6. On "Scopes" page:
   - Click "Add or Remove Scopes"
   - Search for "gmail.send"
   - Check the box for "../auth/gmail.send"
   - Click "Update"
   - Click "Save and Continue"

7. On "Test users" page:
   - Click "Add Users"
   - Enter: romejim@gmail.com
   - Click "Add"
   - Click "Save and Continue"

8. Click "Back to Dashboard"
""")
    input("✓ Done? Press Enter to continue...")

    # Step 4: Create OAuth Credentials
    print_step(4, "Create OAuth2 Credentials")
    print("""
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Job Search Assistant Desktop"
5. Click "Create"
6. Click "Download JSON" (or the download icon)
7. Save the file as: gmail_credentials.json
""")

    credentials_path = Path('config/gmail_credentials.json')
    credentials_path.parent.mkdir(exist_ok=True)

    print(f"""
8. Move the downloaded file to:
   {credentials_path.absolute()}

   You can drag and drop it or use:
   mv ~/Downloads/client_secret_*.json {credentials_path.absolute()}
""")

    while True:
        if credentials_path.exists():
            print(f"\n✅ Credentials file found at {credentials_path}")
            break
        else:
            response = input(f"\n❌ File not found. Have you moved it to {credentials_path}? (yes/no): ")
            if response.lower() == 'no':
                print(f"\nPlease move the downloaded JSON file to: {credentials_path}")
                input("Press Enter when done...")
            else:
                if not credentials_path.exists():
                    print(f"\n❌ Still not found at {credentials_path}")
                    print("Please make sure the file is in the correct location.")

    # Step 5: Test the setup
    print_step(5, "Test Email Authentication")
    print("""
Now we'll test the OAuth2 setup by sending a test email.

A browser window will open asking you to:
1. Select your Google account (romejim@gmail.com)
2. Click "Continue" (you may see a warning - that's OK for testing)
3. Check the box "Send email on your behalf"
4. Click "Continue"

The token will be saved for future use.
""")

    input("Ready to test? Press Enter to continue...")

    # Run test
    try:
        print("\nTesting email service...\n")
        from src.email_service import test_email_service
        test_email_service()

        print_header("✅ Setup Complete!")
        print("""
OAuth2 is now configured and working!

What just happened:
✅ You authorized the app to send emails
✅ A refresh token was saved to config/gmail_token.json
✅ A test email was sent to romejim@gmail.com
✅ Future emails will work automatically (no browser popup)

Security notes:
🔒 No passwords are stored anywhere
🔒 Token is stored locally on your computer
🔒 You can revoke access anytime at: https://myaccount.google.com/permissions
🔒 Token auto-refreshes every hour

Next steps:
1. Check your email inbox for the test message
2. Run the job search: python src/main.py search
3. Set up the scheduler: python src/scheduler.py

You're all set! 🎉
""")

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure gmail_credentials.json is in the config/ folder")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Verify romejim@gmail.com is added as a test user")
        print("\nTry running the setup again or check the documentation.")
        sys.exit(1)


if __name__ == '__main__':
    main()
