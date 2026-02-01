# Simple Setup - Just Do These 3 Things

## Step 1: Get Gmail Credentials (3 minutes)

1. Go here: https://console.cloud.google.com/projectcreate
   - Project name: `JobSearch`
   - Click **Create**

2. Go here: https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - Click **Enable**

3. Go here: https://console.cloud.google.com/apis/credentials/oauthclient
   - Click **Configure Consent Screen**
   - Choose **External** → **Create**
   - App name: `JobSearch`
   - Your email: `romejim@gmail.com`
   - Scroll down → Your email again: `romejim@gmail.com`
   - Click **Save and Continue** 3 times
   - Click **Back to Dashboard**

4. Go here: https://console.cloud.google.com/apis/credentials/oauthclient
   - Application type: **Desktop app**
   - Name: `JobSearch`
   - Click **Create**
   - Click **Download JSON**

5. Move the downloaded file:
   ```bash
   mv ~/Downloads/client_secret_*.json /Users/jimrome/job-search-assistant/config/gmail_credentials.json
   ```

## Step 2: Get AI API Key (1 minute)

Go here: https://console.anthropic.com/settings/keys
- Click **Create Key**
- Copy it

## Step 3: Run Setup (1 minute)

```bash
cd /Users/jimrome/job-search-assistant
./quick_start.sh
```

When it asks for API key, paste the one from Step 2.

Then run:
```bash
python setup_gmail_oauth.py
```

A browser will open → Click **Allow**

**Done!**

Test it:
```bash
python src/main.py search
```

Check your email. You should get a digest.

---

That's it. Those are the only 3 things you need to do.
