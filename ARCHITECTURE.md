# Job Search Assistant - System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     JOB SEARCH ASSISTANT                     │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   SCHEDULER  │──────▶│     MAIN     │──────▶│  EMAIL SENT  │
│  (2x daily)  │       │ ORCHESTRATOR │       │  (to Gmail)  │
└──────────────┘       └──────────────┘       └──────────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │   PROCESSING PIPELINE   │
                └─────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│ JOB FETCHING │      │  AI MATCHING │     │   COMPANY    │
│              │      │              │     │   RESEARCH   │
│ • LinkedIn   │      │ • Score 0-100│     │              │
│ • Indeed     │      │ • Reasoning  │     │ • Contacts   │
│ • Greenhouse │      │ • Cover Lttr │     │ • Insights   │
│ • Lever      │      │ • Gap Analys │     │ • Outreach   │
└──────────────┘      └──────────────┘     └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                      ┌──────────────┐
                      │   DATABASE   │
                      │   (SQLite)   │
                      │              │
                      │ • Jobs       │
                      │ • Companies  │
                      │ • Contacts   │
                      │ • Apps       │
                      └──────────────┘
```

## Component Details

### 1. Resume Parser (`resume_parser.py`)
- **Input**: PDF resumes from `/Users/jimrome/Desktop/Resumes`
- **Output**: Structured data (skills, experience, keywords)
- **Technology**: PyPDF2, pdfplumber
- **Purpose**: Extract Jim's background for matching

### 2. Job Aggregator (`job_aggregator.py`)
- **Input**: Keywords, locations from config
- **Sources**:
  - LinkedIn Jobs API (requires key)
  - Indeed Publisher API (requires key)
  - Greenhouse public API (no key needed)
  - Lever public API (no key needed)
- **Output**: List of job postings
- **Rate Limiting**: Built-in delays to respect API limits

### 3. AI Matcher (`ai_matcher.py`)
- **Input**: Job description + User profile
- **AI Provider**: Anthropic Claude or OpenAI GPT-4
- **Output**:
  - Match score (0-100)
  - Reasoning explanation
  - Cover letter generation
  - Gap analysis
- **Cost**: ~$0.001 per job

### 4. Company Researcher (`company_research.py`)
- **Input**: Company name, job title
- **Output**:
  - Company info (size, funding, industry)
  - Potential contacts (title, LinkedIn URL)
  - Connection reasons
  - Outreach message templates
- **Note**: User sends messages manually (no automation)

### 5. Email Service (`email_service.py`)
- **Input**: Jobs list, digest type (morning/evening)
- **Output**: HTML email to romejim@gmail.com
- **Features**:
  - Beautiful HTML formatting
  - Match scores with color coding
  - Direct links to applications
  - Stats dashboard
- **Delivery**: Gmail SMTP

### 6. Database (`models.py`, `database.py`)
- **Type**: SQLite (local file)
- **Schema**:
  - `jobs`: All job postings
  - `companies`: Company research data
  - `contacts`: Potential connections
  - `applications`: Application tracking
  - `user_profile`: Preferences and settings
  - `email_digests`: Email history

### 7. Scheduler (`scheduler.py`)
- **Technology**: APScheduler
- **Schedule**:
  - 8:00 AM: Morning digest
  - 6:00 PM: Evening digest
- **Deployment**: Can run locally or on cloud

## Data Flow

```
1. SCHEDULER TRIGGERS (8 AM / 6 PM)
   └─▶ Main Orchestrator starts

2. PARSE RESUMES
   └─▶ Extract skills, experience, keywords from PDFs

3. FETCH JOBS
   ├─▶ LinkedIn API → New jobs
   ├─▶ Indeed API → New jobs
   ├─▶ Greenhouse API → New jobs
   └─▶ Lever API → New jobs
   └─▶ Deduplicate & filter existing jobs

4. SCORE JOBS
   └─▶ For each job:
       ├─▶ Send to Claude AI
       ├─▶ Get match score (0-100)
       ├─▶ Get reasoning
       └─▶ Filter by min score (70%)

5. RESEARCH COMPANIES
   └─▶ For top 10 matches:
       ├─▶ Fetch company data
       ├─▶ Identify contacts
       └─▶ Generate outreach templates

6. SAVE TO DATABASE
   ├─▶ Jobs table
   ├─▶ Companies table
   └─▶ Contacts table

7. SEND EMAIL DIGEST
   ├─▶ Build HTML email
   ├─▶ Include top matches
   ├─▶ Include urgent deadlines
   ├─▶ Include contact suggestions
   └─▶ Send via Gmail SMTP

8. DONE
   └─▶ Wait for next scheduled run
```

## Security & Privacy

### What's Stored Locally
- All job data (SQLite database)
- Resume parsed data
- Application history
- Contact suggestions

### What's Sent Externally
- Job search queries → Job board APIs
- Job descriptions → Claude AI (for scoring)
- Email digests → Gmail SMTP

### What's NOT Automated
- LinkedIn connection requests (you send manually)
- Job applications (you click apply)
- Interview scheduling (you handle)
- Follow-up messages (you send)

## Compliance

### LinkedIn
- ✅ Uses official Jobs API only
- ✅ No web scraping
- ✅ No automated messaging
- ✅ Respects rate limits

### Indeed
- ✅ Uses Publisher API
- ✅ Free tier compliant
- ✅ Respects ToS

### Greenhouse/Lever
- ✅ Uses public job board APIs
- ✅ No authentication required
- ✅ Read-only access

## Scalability

### Current Limits
- ~100-200 jobs per day (API limits)
- ~1000 AI scorings per month ($10 budget)
- Unlimited local storage (SQLite)

### If Needed More
- Upgrade LinkedIn API tier ($$$)
- Add more job sources (Glassdoor, ZipRecruiter)
- Use PostgreSQL for cloud database
- Add caching layer (Redis)

## Deployment Options

### Option 1: Local (Free)
- Run on your Mac
- Must keep computer on
- Use cron or scheduler.py

### Option 2: Cloud - Railway ($5/month)
- 24/7 operation
- Auto-deploys from Git
- Managed environment

### Option 3: Cloud - Render (Free tier available)
- Free for background workers
- Limited hours per month
- Good for testing

### Option 4: Cloud - Fly.io (Free tier)
- 3 free VMs
- More technical setup
- Great performance

## File Structure

```
job-search-assistant/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main orchestrator
│   ├── scheduler.py         # 2x daily scheduler
│   ├── models.py            # Database schema
│   ├── database.py          # Database connection
│   ├── resume_parser.py     # Parse PDF resumes
│   ├── job_aggregator.py    # Fetch jobs from APIs
│   ├── ai_matcher.py        # AI-powered matching
│   ├── email_service.py     # Send email digests
│   └── company_research.py  # Research companies
├── config/
│   └── config.yaml          # Configuration
├── data/
│   └── jobs.db             # SQLite database
├── tests/                   # (Future: unit tests)
├── .env                     # Environment variables (SECRET)
├── .env.example            # Template for .env
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── README.md              # User guide
├── ARCHITECTURE.md        # This file
├── Procfile               # Cloud deployment config
├── runtime.txt            # Python version
└── quick_start.sh         # Setup script
```

## Future Enhancements

### Phase 2 (Next)
- [ ] Web dashboard (Flask/FastAPI)
- [ ] Browser extension (Chrome/Firefox)
- [ ] Salary negotiation insights
- [ ] Interview prep assistant

### Phase 3 (Future)
- [ ] Machine learning for better matching
- [ ] Application success analytics
- [ ] Network graph of connections
- [ ] Calendar integration for interviews

## Monitoring & Logs

### Logs Location
- Console output: `STDOUT`
- File: `job_search.log`
- Database queries: Enable `echo=True` in database.py

### Health Checks
```bash
# Check if scheduler is running
ps aux | grep scheduler.py

# Check last run
tail -f job_search.log

# Check database
sqlite3 data/jobs.db "SELECT COUNT(*) FROM jobs;"

# Check email status
# (Look for ✓ Email sent in logs)
```

## Troubleshooting

### Common Issues

1. **No jobs found**
   - Check API keys in .env
   - Try Greenhouse/Lever only (no keys needed)

2. **AI scoring errors**
   - Verify ANTHROPIC_API_KEY
   - Check API credits

3. **Email not sending**
   - Verify Gmail App Password
   - Check 2FA enabled

4. **Database locked**
   - Only run one instance
   - Check for zombie processes

---

**Built with ❤️ for Product Managers searching for their next role**
