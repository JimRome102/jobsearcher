# Job Search Assistant

An automated, **legal and ToS-compliant** job search assistant that finds, scores, and tracks job opportunities tailored to your background.

## Features

- **Multi-Source Job Aggregation**: Fetches jobs from LinkedIn, Indeed, Greenhouse, Lever, and more
- **AI-Powered Matching**: Uses Claude/GPT to score jobs against your profile (0-100 score)
- **Company Research**: Identifies potential contacts and gathers company insights
- **2x Daily Email Digests**: Morning and evening updates with top matches
- **Application Tracking**: Track applications, interviews, and follow-ups
- **Smart Recommendations**: Suggests contacts to reach out to (you send manually)
- **Cover Letter Generator**: AI-generated tailored cover letters
- **All Legal & Compliant**: Uses only official APIs and public data

## What This System Does

### Automated (No Action Required)
- ✅ Fetches new jobs every 12 hours
- ✅ Scores each job against your profile
- ✅ Researches companies and identifies contacts
- ✅ Sends you email digests with top matches
- ✅ Tracks all jobs in a database

### Semi-Automated (You Review & Click)
- 👤 You review job matches in emails
- 👤 You click "Apply" on job sites
- 👤 You send LinkedIn connection requests to suggested contacts
- 👤 You mark jobs as applied/rejected in the system

## Setup Instructions

### 1. Prerequisites

- Python 3.9+ installed
- A code editor (VS Code, PyCharm, etc.)
- Gmail account for receiving digests

### 2. Clone or Download This Repository

```bash
cd /Users/jimrome/job-search-assistant
```

### 3. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Set Up API Keys

You'll need API keys for:

#### A. AI Service (Choose ONE)

**Option 1: Anthropic Claude (Recommended)**
1. Sign up at https://console.anthropic.com/
2. Create an API key
3. Free tier: $5 credit (good for ~5000 job matches)
4. Cost: ~$0.001 per job scored

**Option 2: OpenAI GPT-4**
1. Sign up at https://platform.openai.com/
2. Create an API key
3. Cost: ~$0.002 per job scored

#### B. Job Board APIs (Optional but Recommended)

**LinkedIn Jobs API** (Free tier available)
- Sign up: https://developer.linkedin.com/
- Create app and get API key
- Free tier: 100 requests/day

**Indeed Publisher API** (Free)
- Sign up: https://opensource.indeedeng.io/api-documentation/
- Get publisher ID
- Free tier: 200 requests/day

#### C. Gmail OAuth2 (For Email Digests - Secure!)

We use OAuth2 instead of passwords for better security.

**Quick Setup:**
```bash
python setup_gmail_oauth.py
```

This script will guide you through:
1. Creating a Google Cloud project
2. Enabling Gmail API
3. Setting up OAuth2 credentials
4. Testing email sending

**Manual Setup** (if you prefer):
1. Go to https://console.cloud.google.com/
2. Create new project "Job Search Assistant"
3. Enable Gmail API
4. Create OAuth2 credentials (Desktop app)
5. Download credentials to `config/gmail_credentials.json`
6. Run `python setup_gmail_oauth.py` to complete setup

### 5. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use any text editor
```

Fill in your keys:
```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxxxx  # OR OpenAI key
USER_EMAIL=romejim@gmail.com

# Email - configured via OAuth2 (no password needed!)
USER_EMAIL=romejim@gmail.com

# Optional (for more job sources)
LINKEDIN_API_KEY=your_linkedin_key
INDEED_API_KEY=your_indeed_key

# Job preferences
MIN_SALARY=150000
MAX_SALARY=300000
PREFERRED_LOCATIONS=New York,Remote,San Francisco
PREFERRED_ROLES=Principal Product Manager,Director of Product,VP Product
```

### 6. Test the System

Run a one-time job search to test everything works:

```bash
python src/main.py search
```

This will:
1. Parse your resumes from `/Users/jimrome/Desktop/Resumes`
2. Fetch jobs from available sources
3. Score each job with AI
4. Save to database
5. Send you an email digest

### 7. View Results

Check your email (romejim@gmail.com) for the digest!

You can also check the database:
```bash
python src/main.py summary
```

### 8. Generate Application Materials

When you find a job you like, generate tailored materials:

```bash
python src/main.py apply <job_id>
```

This generates:
- Tailored cover letter
- Key preparation points
- Suggested contacts to reach out to
- LinkedIn message templates

## Running Automatically (2x Daily)

### Option A: Run Locally on Your Computer

Keep the scheduler running on your computer:

```bash
python src/scheduler.py
```

This runs the job search at:
- 8:00 AM (Morning digest)
- 6:00 PM (Evening digest)

**Note**: Your computer must be on and running.

### Option B: Deploy to Cloud (Recommended)

For 24/7 operation, deploy to a cloud service:

#### Using Railway (Easiest, ~$5/month)

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Connect your repository
4. Add environment variables in Railway dashboard
5. Railway will auto-run the scheduler

#### Using Render (Free Tier Available)

1. Sign up at https://render.com
2. Create new "Background Worker"
3. Connect repository
4. Set start command: `python src/scheduler.py`
5. Add environment variables
6. Deploy

#### Using Fly.io (Free tier: 3 small VMs)

1. Install flyctl: `brew install flyctl`
2. Sign up: `fly auth signup`
3. Launch: `fly launch`
4. Add secrets: `fly secrets set ANTHROPIC_API_KEY=xxx ...`
5. Deploy: `fly deploy`

### Option C: Use Cron (Mac/Linux)

Add to your crontab:
```bash
crontab -e

# Add these lines:
0 8 * * * cd /Users/jimrome/job-search-assistant && /Users/jimrome/job-search-assistant/venv/bin/python src/main.py search
0 18 * * * cd /Users/jimrome/job-search-assistant && /Users/jimrome/job-search-assistant/venv/bin/python src/main.py search
```

## Cost Breakdown

### Free Tier (Limited)
- Greenhouse/Lever APIs: Free
- Indeed API: Free (200 requests/day)
- Email: Free (Gmail)
- **Total**: $0/month
- **Limitation**: Fewer job sources, need API keys

### Recommended Setup (~$15-20/month)
- Anthropic API: ~$10/month (1000 jobs scored)
- LinkedIn API: Free tier (100 requests/day)
- Cloud hosting (Railway/Render): $5-10/month
- **Total**: $15-20/month
- **Gets you**: Full automation, all job sources, reliable 24/7 operation

## Usage Guide

### Daily Workflow

1. **Morning (8 AM)**: Check email for morning digest
2. **Review top matches**: Click through to jobs that interest you
3. **Research companies**: Use provided contact suggestions
4. **Apply**: Generate materials with `python src/main.py apply <id>`
5. **Evening (6 PM)**: Check email for evening digest
6. **Weekly**: Review application status, send follow-ups

### Email Digest Contents

Each digest includes:
- **Stats**: New matches, high matches, urgent applications
- **Top Matches**: 5 best jobs with AI reasoning
- **More Opportunities**: 5 additional good matches
- **Match Score**: 0-100 score for each job
- **Why It Matches**: AI explanation of fit
- **Direct Links**: Click to view job postings

### Viewing All Jobs

```bash
# Get summary
python src/main.py summary

# Query database directly
sqlite3 data/jobs.db
> SELECT title, company, match_score FROM jobs ORDER BY match_score DESC LIMIT 10;
```

### Updating Your Profile

Edit `config/config.yaml` to update:
- Skills
- Preferences
- Target roles
- Excluded keywords

## Database Schema

The system tracks:
- **Jobs**: Title, company, description, match score, status
- **Companies**: Research data, funding, size, culture
- **Contacts**: Potential connections at companies
- **Applications**: Application status, dates, notes
- **User Profile**: Your preferences and settings

## Troubleshooting

### "No jobs found"
- Check API keys are set correctly
- Try running with just Greenhouse/Lever (no API keys needed)
- Check your keyword filters in config.yaml

### "Email not sending"
- Run OAuth2 setup: `python setup_gmail_oauth.py`
- Check Gmail API is enabled in Google Cloud Console
- Verify credentials file exists: `config/gmail_credentials.json`
- Test: `python -c "from src.email_service import test_email_service; test_email_service()"`

### "AI scoring errors"
- Verify ANTHROPIC_API_KEY or OPENAI_API_KEY is set
- Check you have API credits remaining
- Try with a smaller batch of jobs first

### "Database locked"
- Only run one instance at a time
- If stuck: `rm data/jobs.db` (will delete all data)

## Privacy & Security

- ✅ All data stored locally (SQLite database)
- ✅ API keys stored in `.env` (never committed to git)
- ✅ OAuth2 for Gmail (no passwords stored, tokens auto-refresh)
- ✅ No data sent to third parties (except job board APIs and AI scoring)
- ✅ You control all outreach (no auto-messaging)
- ✅ Compliant with all platform Terms of Service
- ✅ Can revoke access anytime at https://myaccount.google.com/permissions

## Future Enhancements

Potential additions:
- [ ] Web dashboard to view/manage jobs
- [ ] Slack/Discord notifications
- [ ] Interview scheduling assistant
- [ ] Salary negotiation insights
- [ ] Application success analytics
- [ ] Chrome extension for one-click apply

## Support

Questions? Issues?
- Check logs: `tail -f job_search.log`
- Database issues: Check `data/jobs.db`
- Email: romejim@gmail.com

## License

MIT License - Free to use and modify

---

**Built with**: Python, SQLAlchemy, Claude AI, APScheduler

**Author**: Jim Rome

**Version**: 1.0.0
