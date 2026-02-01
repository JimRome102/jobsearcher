# Gmail OAuth2 Setup Guide

## Why OAuth2 Instead of App Passwords?

**Security Benefits:**
- 🔒 No passwords stored anywhere (tokens are used instead)
- 🔒 Granular permissions (only "send email" access)
- 🔒 Can be revoked instantly from your Google Account
- 🔒 Tokens auto-refresh securely
- 🔒 Industry-standard authentication (used by all major apps)

**Convenience:**
- ✅ Set up once, works forever
- ✅ No need to remember passwords
- ✅ Works even if you change your Gmail password

---

## Quick Setup (Recommended)

Run the automated setup script:

```bash
cd /Users/jimrome/job-search-assistant
python setup_gmail_oauth.py
```

The script will guide you through each step interactively.

---

## Manual Setup Instructions

### Step 1: Create Google Cloud Project (2 minutes)

1. Visit: https://console.cloud.google.com/
2. Click **"Select a project"** (top bar) → **"New Project"**
3. Project name: `Job Search Assistant`
4. Click **"Create"**
5. Wait for notification that project is created

---

### Step 2: Enable Gmail API (1 minute)

1. Visit: https://console.cloud.google.com/apis/library
2. Search for: `Gmail API`
3. Click on **"Gmail API"** in results
4. Click **"Enable"**
5. Wait for API to be enabled

---

### Step 3: Configure OAuth Consent Screen (3 minutes)

1. Visit: https://console.cloud.google.com/apis/credentials/consent

2. **Choose user type:**
   - Select **"External"**
   - Click **"Create"**

3. **Fill in OAuth consent screen:**
   - App name: `Job Search Assistant`
   - User support email: `romejim@gmail.com`
   - Developer contact: `romejim@gmail.com`
   - Click **"Save and Continue"**

4. **Add scopes:**
   - Click **"Add or Remove Scopes"**
   - Search for: `gmail.send`
   - Check the box: `https://www.googleapis.com/auth/gmail.send`
   - Click **"Update"**
   - Click **"Save and Continue"**

5. **Add test users:**
   - Click **"Add Users"**
   - Enter: `romejim@gmail.com`
   - Click **"Add"**
   - Click **"Save and Continue"**

6. Click **"Back to Dashboard"**

---

### Step 4: Create OAuth2 Credentials (2 minutes)

1. Visit: https://console.cloud.google.com/apis/credentials

2. Click **"Create Credentials"** → **"OAuth client ID"**

3. **Configure OAuth client:**
   - Application type: **"Desktop app"**
   - Name: `Job Search Assistant Desktop`
   - Click **"Create"**

4. **Download credentials:**
   - Click **"Download JSON"** (download icon)
   - A file like `client_secret_xxxxx.json` will download

5. **Move the file:**
   ```bash
   # Rename and move to correct location
   mv ~/Downloads/client_secret_*.json /Users/jimrome/job-search-assistant/config/gmail_credentials.json
   ```

---

### Step 5: Authorize and Test (1 minute)

1. **Run the setup script:**
   ```bash
   python setup_gmail_oauth.py
   ```

2. **Browser will open automatically:**
   - Select your Google account: `romejim@gmail.com`
   - You may see: "Google hasn't verified this app"
     - Click **"Advanced"** → **"Go to Job Search Assistant (unsafe)"**
     - (This is safe - it's your own app!)
   - Review permissions: "Send email on your behalf"
   - Click **"Allow"**

3. **Authorization complete!**
   - Browser will show: "The authentication flow has completed"
   - Token saved to: `config/gmail_token.json`
   - Test email sent to: `romejim@gmail.com`

---

## File Structure After Setup

```
config/
├── gmail_credentials.json  ← OAuth2 app credentials (keep secret!)
└── gmail_token.json        ← Access token (auto-refreshes)
```

**Important:**
- Both files are in `.gitignore` (won't be committed)
- Keep `gmail_credentials.json` secret
- `gmail_token.json` auto-refreshes every hour
- Delete `gmail_token.json` to re-authorize

---

## Testing the Setup

### Send a Test Email

```bash
python -c "from src.email_service import test_email_service; test_email_service()"
```

You should receive a test email at `romejim@gmail.com`

### Check Token Status

```bash
# View token file (contains refresh token)
cat config/gmail_token.json | python -m json.tool
```

---

## Troubleshooting

### "Credentials file not found"

Make sure the file is at the correct location:
```bash
ls -la config/gmail_credentials.json
```

If not found, download again from Google Cloud Console.

### "Access blocked: This app's request is invalid"

This means OAuth consent screen is not configured correctly:
1. Go to https://console.cloud.google.com/apis/credentials/consent
2. Make sure `romejim@gmail.com` is added as a test user
3. Make sure `gmail.send` scope is added

### "Refresh token expired"

Delete the token and re-authorize:
```bash
rm config/gmail_token.json
python setup_gmail_oauth.py
```

### "Gmail API has not been used in project"

Enable the Gmail API:
1. Visit: https://console.cloud.google.com/apis/library
2. Search for "Gmail API"
3. Click "Enable"

---

## Security Best Practices

### ✅ What's Safe
- Sharing `gmail_token.json` is OK (it's your personal token)
- Token auto-refreshes every hour
- Can revoke access anytime

### ❌ Keep Secret
- Never share `gmail_credentials.json` (contains client secrets)
- Don't commit to Git (already in `.gitignore`)
- Don't publish publicly

### 🔒 Revoking Access

If you ever want to revoke access:

1. Visit: https://myaccount.google.com/permissions
2. Find "Job Search Assistant"
3. Click "Remove Access"
4. Delete local token: `rm config/gmail_token.json`

---

## How OAuth2 Works

```
┌─────────────┐
│   Your App  │
└──────┬──────┘
       │ 1. Request authorization
       ▼
┌─────────────┐
│   Google    │ ← You log in and approve
└──────┬──────┘
       │ 2. Return authorization code
       ▼
┌─────────────┐
│   Your App  │
└──────┬──────┘
       │ 3. Exchange code for tokens
       ▼
┌─────────────┐
│   Google    │
└──────┬──────┘
       │ 4. Return access token + refresh token
       ▼
┌─────────────┐
│   Your App  │ ← Saves tokens to gmail_token.json
└──────┬──────┘
       │ 5. Use access token to send emails
       ▼
┌─────────────┐
│  Gmail API  │ ← Emails sent successfully!
└─────────────┘

Every hour:
- Access token expires
- App uses refresh token to get new access token
- No user interaction needed!
```

---

## Next Steps

After setup is complete:

1. ✅ Test email works: `python -c "from src.email_service import test_email_service; test_email_service()"`

2. ✅ Set up AI API keys in `.env`:
   ```bash
   nano .env
   # Add: ANTHROPIC_API_KEY=sk-ant-xxxxx
   ```

3. ✅ Run first job search:
   ```bash
   python src/main.py search
   ```

4. ✅ Start scheduler (2x daily):
   ```bash
   python src/scheduler.py
   ```

---

## Support

If you encounter any issues:

1. Check this guide's troubleshooting section
2. Review logs: `tail -f job_search.log`
3. Re-run setup: `python setup_gmail_oauth.py`
4. Check Google Cloud Console for any alerts

**Common Issue:** "This app hasn't been verified"
- This is expected for personal apps
- Click "Advanced" → "Go to Job Search Assistant (unsafe)"
- This is safe because you created the app yourself

---

**You're all set! OAuth2 is much more secure than app passwords. 🔒**
