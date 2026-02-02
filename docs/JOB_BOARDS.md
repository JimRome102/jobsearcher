# Job Boards Integration

This document describes all supported job boards and their integration status.

## Integration Status

| Job Board | Status | Type | API Required | Notes |
|-----------|--------|------|--------------|-------|
| LinkedIn | ⚠️ Partial | API | Yes | 401 errors, needs valid API key |
| Indeed | ⚠️ Partial | API | Yes | DNS errors, needs valid API key |
| Greenhouse | ✅ Working | API | No | Public API, multiple companies |
| Lever | ⚠️ Partial | API | No | Public API, low results |
| Glassdoor | 🚧 Planned | Web | No | RSS feed scraping planned |
| Built In | 🚧 Planned | Web | No | Web scraping planned |
| Wellfound | 🚧 Ready | API | Yes | GraphQL API, needs key |
| YC Jobs | 🚧 Planned | Web | No | Web scraping planned |
| Remote OK | ✅ Ready | API | No | Public API available |
| We Work Remotely | ✅ Ready | RSS | No | RSS feed available |
| Mind the Product | 🚧 Planned | Web | No | Job board scraping |
| Otta | 🚧 Planned | API | Yes | Requires authentication |
| Dice | 🚧 Planned | Web | No | Web scraping planned |

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

## Currently Working Sources

As of now, these sources are actively fetching jobs:
1. **Greenhouse** - 20 companies, public API
2. **Remote OK** - Ready to use (public API)
3. **We Work Remotely** - Ready to use (RSS)

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
