# Quick Reference

## Setup (First Time Only)
```bash
./easy_setup.sh
```

## Commands

```bash
# Run job search once
python src/main.py search

# View all jobs
python src/main.py summary

# Generate cover letter for a job
python src/main.py apply <job_id>

# Start automated 2x daily (8am & 6pm)
python src/scheduler.py
```

## What You Get

**2x Daily Emails** to romejim@gmail.com with:
- Top 10 job matches
- AI match scores (0-100)
- Why each job matches you
- Suggested contacts at each company
- Direct apply links

## Files

```
config/gmail_credentials.json  ← Don't share this
config/gmail_token.json        ← Auto-refreshes
.env                          ← Your API keys
data/jobs.db                  ← All job data
```

## View Jobs in Database

```bash
sqlite3 data/jobs.db
> SELECT title, company, match_score FROM jobs ORDER BY match_score DESC LIMIT 10;
```

## Costs

- AI scoring: ~$10/month
- Cloud hosting (optional): $5/month
- Everything else: Free

## Support

- Setup issues: Re-run `./easy_setup.sh`
- Check logs: `tail -f job_search.log`
- Test email: `python -c "from src.email_service import test_email_service; test_email_service()"`

## Security

- OAuth2 (no passwords stored)
- All data local
- Revoke access anytime: https://myaccount.google.com/permissions
