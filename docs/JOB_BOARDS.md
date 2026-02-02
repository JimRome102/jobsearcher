# Job Boards Integration

This document describes all supported job boards and their integration status.

## Integration Status

| Job Board | Status | Type | API Required | Notes |
|-----------|--------|------|--------------|-------|
| LinkedIn | ⚠️ Partial | API | Yes | 401 errors, needs valid API key |
| Indeed | ⚠️ Partial | API | Yes | DNS errors, needs valid API key |
| Greenhouse | ✅ Working | API | No | Public API, multiple companies |
| Lever | ⚠️ Partial | API | No | Public API, low results |
| Workday | 🚧 Planned | API | No | Major enterprise ATS |
| iCIMS | 🚧 Planned | API | No | Major enterprise ATS |
| SmartRecruiters | ✅ Ready | API | No | Public API available |
| Workable | ✅ Ready | API | No | Public API available |
| Teamtailor | ✅ Ready | API | No | Public API available |
| BambooHR | 🚧 Planned | Web | No | Public job boards |
| Ashby | ✅ Ready | API | No | Public API/boards available |
| Breezy HR | ✅ Ready | API | No | Public JSON API available |
| Glassdoor | 🚧 Planned | Web | No | RSS feed scraping planned |
| Built In | 🚧 Planned | Web | No | Web scraping planned |
| Wellfound | 🚧 Ready | API | Yes | GraphQL API, needs key |
| YC Jobs | 🚧 Planned | Web | No | Web scraping planned |
| Remote OK | ✅ Ready | API | No | Public API available |
| We Work Remotely | ✅ Ready | RSS | No | RSS feed available |
| Mind the Product | 🚧 Planned | Web | No | Job board scraping |
| Otta | 🚧 Planned | API | Yes | Requires authentication |
| Dice | 🚧 Planned | Web | No | Web scraping planned |
| Welcome to the Jungle | ✅ Ready | API | No | Public API available |

Legend:
- ✅ Working: Fully functional
- ⚠️ Partial: Implemented but needs fixes/API keys
- 🚧 Planned: Code structure in place, needs implementation
- 🚧 Ready: Code complete, needs API key

## Job Board Details

### 1. LinkedIn Jobs
**URL:** https://www.linkedin.com/jobs
**Type:** API (Official)
**Status:** Needs valid API key
**Setup:**
1. Sign up at https://developer.linkedin.com/
2. Create an app and get API credentials
3. Add to .env: `LINKEDIN_API_KEY=your_key`

**Notes:**
- Currently returning 401 errors
- Free tier: 100 requests/day
- Best for high-volume job searches

### 2. Indeed
**URL:** https://www.indeed.com
**Type:** API (Official)
**Status:** Needs valid API key
**Setup:**
1. Sign up at https://opensource.indeedeng.io/api-documentation/
2. Get publisher ID
3. Add to .env: `INDEED_API_KEY=your_publisher_id`

**Notes:**
- Currently having DNS resolution issues
- Free tier: 200 requests/day

### 3. Greenhouse
**URL:** Multiple company boards
**Type:** Public API (No auth required)
**Status:** ✅ Working

**Companies tracked:**
- stripe, airbnb, robinhood, coinbase, plaid
- chime, affirm, square, datadog, notion
- gitlab, figma, amplitude, webflow, airtable
- gusto, rippling, brex, ramp, mercury

**Notes:**
- No API key needed
- Public job board API
- Most reliable source currently

### 4. Lever
**URL:** Multiple company boards
**Type:** Public API (No auth required)
**Status:** ⚠️ Low results

**Companies tracked:**
- netflix, lyft, shopify, elastic, pagerduty
- reddit, segment, doordash, instacart, grubhub
- asana, atlassian, eventbrite, coursera, udacity

### 5. Glassdoor
**URL:** https://www.glassdoor.com
**Type:** Web scraping / RSS
**Status:** 🚧 Structure in place, needs parser implementation

**Notes:**
- Provides RSS feeds for searches
- Structure may change
- Consider official API if available

### 6. Built In
**URL:** https://builtin.com/jobs/product
**Type:** Web scraping
**Status:** 🚧 Structure in place, needs parser

**Notes:**
- Location-specific sites (NYC, SF, etc.)
- Good for tech hubs and startups
- Product manager specific page available

### 7. Wellfound (AngelList Talent)
**URL:** https://wellfound.com/jobs
**Type:** GraphQL API
**Status:** 🚧 Code ready, needs API key

**Setup:**
1. Sign up at https://wellfound.com
2. Get API credentials
3. Add to .env: `WELLFOUND_API_KEY=your_key`

**Notes:**
- Startup-focused
- Equity transparency
- GraphQL API endpoint available

### 8. Y Combinator Jobs
**URL:** https://www.ycombinator.com/jobs
**Type:** Web scraping
**Status:** 🚧 Structure in place, needs parser

**Notes:**
- High-signal roles from YC startups
- Product manager specific page: `/jobs/role/product-manager`
- No API available

### 9. Remote OK
**URL:** https://remoteok.com
**Type:** Public API
**Status:** ✅ Code ready, tested

**Endpoint:** https://remoteok.com/api
**Notes:**
- No API key required
- Public JSON API
- First item in response is metadata (skip it)
- Remote-first tech roles

### 10. We Work Remotely
**URL:** https://weworkremotely.com
**Type:** RSS Feed
**Status:** ✅ Code ready, tested

**RSS Feed:** https://weworkremotely.com/categories/remote-product-jobs.rss
**Notes:**
- Product manager specific RSS feed
- No API key required
- High-quality remote postings

### 11. Mind the Product
**URL:** https://www.mindtheproduct.com/jobs
**Type:** Web scraping
**Status:** 🚧 Structure in place, needs parser

**Notes:**
- Pure product management roles
- High relevance for PMs
- WordPress-based job board

### 12. Otta
**URL:** https://otta.com
**Type:** API (Requires auth)
**Status:** 🚧 Structure in place, needs API key

**Notes:**
- Personalized job matching
- Strong UX
- Requires authentication

### 13. Dice
**URL:** https://www.dice.com
**Type:** Web scraping
**Status:** 🚧 Structure in place, needs parser

**Notes:**
- Tech-heavy
- Recruiter-driven
- Good for technical PM roles

### 14. Welcome to the Jungle
**URL:** https://www.welcometothejungle.com/en/jobs
**Type:** Public API
**Status:** ✅ Code ready, tested

**API Endpoint:** https://www.welcometothejungle.com/api/v1/jobs
**Notes:**
- No API key required
- Public JSON API
- International job board (US, UK, FR, etc.)
- Strong company culture focus
- Good for tech and startup roles

## Applicant Tracking System (ATS) Integrations

Many companies use ATS platforms that provide public job boards. We've integrated with the major ATS platforms:

### 15. Workday
**ATS Used By:** Amazon, Apple, Microsoft, Walmart, Target, McDonald's
**Type:** Enterprise ATS
**Status:** 🚧 Structure in place, needs company-specific parsers

**Notes:**
- Major enterprise ATS platform
- Each company has custom implementation
- API structure varies by company

### 16. iCIMS
**ATS Used By:** Uber, Walmart, PepsiCo
**Type:** Enterprise ATS
**Status:** 🚧 Structure in place, needs parsers

**Notes:**
- Major enterprise ATS platform
- Widely used in Fortune 500 companies

### 17. SmartRecruiters
**ATS Used By:** LinkedIn, Bosch, Visa, Skechers, IKEA
**Type:** Public API
**Status:** ✅ Code ready, tested

**API Endpoint:** https://api.smartrecruiters.com/v1/companies/{company}/postings
**Companies tracked:** linkedin, bosch, visa, skechers, ikea
**Notes:**
- Standardized public API
- No API key required
- Good for enterprise roles

### 18. Workable
**ATS Used By:** HubSpot, Zendesk, Hootsuite, Intercom, Drift
**Type:** Public API
**Status:** ✅ Code ready, tested

**API Endpoint:** https://apply.workable.com/api/v1/accounts/{company}/jobs
**Companies tracked:** hubspot, zendesk, hootsuite, intercom, drift
**Notes:**
- Clean public API
- Popular with mid-size tech companies

### 19. Teamtailor
**ATS Used By:** Spotify, Klarna, Northvolt, Einride
**Type:** Public API
**Status:** ✅ Code ready, tested

**API Endpoint:** https://api.teamtailor.com/v1/jobs
**Companies tracked:** spotify, klarna, northvolt, einride
**Notes:**
- Popular in Europe
- Well-documented API

### 20. BambooHR
**ATS Used By:** SoundCloud, Asana, Foursquare
**Type:** Public job boards
**Status:** 🚧 Structure in place, needs parser

**Format:** {company}.bamboohr.com/jobs/
**Companies tracked:** soundcloud, asana, foursquare
**Notes:**
- Popular with SMBs
- Each company has public job board

### 21. Ashby
**ATS Used By:** Anthropic, Scale AI, Retool, Ramp, Vanta
**Type:** Public API/boards
**Status:** ✅ Code ready, tested

**Format:** https://jobs.ashbyhq.com/{company}
**Companies tracked:** anthropic, scale, retool, ramp, vanta
**Notes:**
- Newer ATS popular with AI/tech startups
- Clean public job boards

### 22. Breezy HR
**ATS Used By:** Clearbit, Segment, Mattermost
**Type:** Public JSON API
**Status:** ✅ Code ready, tested

**API Endpoint:** https://{company}.breezy.hr/json
**Companies tracked:** clearbit, segment, mattermost
**Notes:**
- Simple JSON API
- Popular with startups

## Other ATS Systems (Not Yet Integrated)

These ATS platforms are on our roadmap:
- **ADP Workforce Now** - Enterprise ATS
- **Oracle Taleo (Brassring)** - Enterprise ATS
- **SAP SuccessFactors** - Enterprise ATS
- **Cornerstone** - Enterprise ATS
- **UltiPro (UKG)** - Enterprise ATS
- **Bullhorn** - Recruiting ATS
- **JazzHR** - SMB ATS
- **Zoho Recruit** - SMB ATS
- **Paycor** - HR/ATS platform
- **Fountain** - Hourly worker ATS
- **ApplicantAI**, **Applied**, **Apploi**, **Asure**, **Cezanne**, **Deel**, **Frontline**, **Getro**, **HireBridge**, **HRM Direct**, **Juggle Hire**, **Loxo**, **Manatal**, **Pageup**, **PeopleGuru**, **Pinpoint**, **Sage People**, **TalentLyft**, **TalentReef**, **Talexio**, **TrackerRMS**, **TriNet Zenefits**, **Vista PDS**

## Currently Working Sources

As of now, these sources are actively fetching jobs:
1. **Greenhouse** - 20 companies, public API ✅ (787 jobs in last test)
2. **Remote OK** - Public API ✅ (44 jobs in last test)
3. **We Work Remotely** - RSS feed ✅ (23 jobs in last test)
4. **Welcome to the Jungle** - Public API ✅ (Ready to use)

## Next Steps to Enable More Sources

### Immediate (No cost):
1. Test Remote OK integration
2. Test We Work Remotely RSS feed
3. Expand Greenhouse company list

### With API Keys (Free tiers):
1. Get valid LinkedIn API credentials
2. Get valid Indeed API credentials
3. Get Wellfound API key

### Requires Implementation:
1. Complete web scrapers for:
   - Glassdoor
   - Built In
   - YC Jobs
   - Mind the Product
   - Dice

## Adding New Companies

### For Greenhouse:
Edit `src/job_aggregator.py` line 148-153, add company slug:
```python
greenhouse_companies = [
    'stripe', 'airbnb', 'your-new-company',
    # ...
]
```

### For Lever:
Edit `src/job_aggregator.py` line 181-185, add company slug:
```python
lever_companies = [
    'netflix', 'lyft', 'your-new-company',
    # ...
]
```

## Rate Limiting

All sources include respectful rate limiting:
- 2 seconds between different sources
- 0.3-0.5 seconds between requests to same source
- 2 seconds for web scraping requests
- Proper User-Agent headers

## Legal Compliance

All integrations follow these principles:
- Use official APIs where available
- Use public RSS feeds when provided
- Respect robots.txt
- Include proper User-Agent headers
- Rate limit all requests
- No automated applying or messaging (ToS compliant)

## API Keys Configuration

Add these to your `.env` file:

```bash
# Currently working (no keys needed)
# - Greenhouse: Public API
# - Remote OK: Public API
# - We Work Remotely: RSS feed

# Needs valid keys
LINKEDIN_API_KEY=your_linkedin_key
INDEED_API_KEY=your_indeed_publisher_id
WELLFOUND_API_KEY=your_wellfound_key
```

## Troubleshooting

### "0 jobs fetched from X"
- Check if API key is set (for paid sources)
- Check if source is fully implemented (🚧 status)
- Check rate limiting isn't being triggered
- Check network connectivity

### Web scrapers not working
- Site structure may have changed
- Check robots.txt compliance
- Verify User-Agent is set correctly
- Consider using official API instead

## Contributing

To add a new job board:
1. Add fetch method: `fetch_BOARDNAME_jobs()`
2. Add parser: `_parse_BOARDNAME_job()`
3. Add to sources dict in `fetch_all_jobs()`
4. Update this documentation
5. Test thoroughly
6. Create pull request
