"""Job aggregation service to fetch jobs from multiple sources."""

import os
import time
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict
import requests
from bs4 import BeautifulSoup


class JobAggregator:
    """Aggregate jobs from multiple sources."""

    def __init__(self, config: Dict):
        """Initialize job aggregator."""
        self.config = config
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY')
        self.indeed_api_key = os.getenv('INDEED_API_KEY')
        self.wellfound_api_key = os.getenv('WELLFOUND_API_KEY')

        # User agent for web scraping
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }

    def fetch_all_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from all enabled sources."""
        all_jobs = []

        # Fetch from each source
        sources = {
            'linkedin': self.fetch_linkedin_jobs,
            'indeed': self.fetch_indeed_jobs,
            'greenhouse': self.fetch_greenhouse_jobs,
            'lever': self.fetch_lever_jobs,
            'workday': self.fetch_workday_jobs,
            'icims': self.fetch_icims_jobs,
            'smartrecruiters': self.fetch_smartrecruiters_jobs,
            'workable': self.fetch_workable_jobs,
            'teamtailor': self.fetch_teamtailor_jobs,
            'bamboohr': self.fetch_bamboohr_jobs,
            'ashby': self.fetch_ashby_jobs,
            'breezyhr': self.fetch_breezyhr_jobs,
            'glassdoor': self.fetch_glassdoor_jobs,
            'builtin': self.fetch_builtin_jobs,
            'wellfound': self.fetch_wellfound_jobs,
            'yc_jobs': self.fetch_yc_jobs,
            'remoteok': self.fetch_remoteok_jobs,
            'weworkremotely': self.fetch_weworkremotely_jobs,
            'mindtheproduct': self.fetch_mindtheproduct_jobs,
            'otta': self.fetch_otta_jobs,
            'dice': self.fetch_dice_jobs,
            'welcometothejungle': self.fetch_welcometothejungle_jobs,
            'productjobs': self.fetch_productjobs_jobs,
            'trueup': self.fetch_trueup_jobs,
            'pave': self.fetch_pave_jobs,
            'hiringcafe': self.fetch_hiringcafe_jobs,
        }

        for source_name, fetch_func in sources.items():
            try:
                jobs = fetch_func(keywords, locations)
                print(f"✓ Fetched {len(jobs)} jobs from {source_name}")
                all_jobs.extend(jobs)
                time.sleep(2)  # Rate limiting between sources
            except Exception as e:
                print(f"✗ Error fetching from {source_name}: {e}")

        # Deduplicate jobs
        all_jobs = self._deduplicate_jobs(all_jobs)

        print(f"\n✓ Total unique jobs fetched: {len(all_jobs)}")
        return all_jobs

    def fetch_linkedin_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from LinkedIn Jobs API."""
        jobs = []

        # LinkedIn Jobs API (requires API key)
        # Note: This uses the official LinkedIn Jobs API
        # Free tier available at: https://developer.linkedin.com/

        if not self.linkedin_api_key:
            return jobs

        for keyword in keywords:
            for location in locations:
                try:
                    url = "https://api.linkedin.com/v2/jobs"
                    params = {
                        'keywords': keyword,
                        'location': location,
                        'limit': 50,
                    }
                    headers = {
                        'Authorization': f'Bearer {self.linkedin_api_key}',
                        'X-Restli-Protocol-Version': '2.0.0',
                    }

                    response = requests.get(url, params=params, headers=headers)

                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get('elements', []):
                            jobs.append(self._parse_linkedin_job(job))
                    else:
                        print(f"LinkedIn API returned status {response.status_code}")

                    time.sleep(0.5)  # Rate limiting

                except Exception as e:
                    print(f"Error fetching LinkedIn jobs: {e}")

        return jobs

    def fetch_indeed_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Indeed API."""
        jobs = []

        # Indeed API (requires publisher ID)
        # Free tier available at: https://opensource.indeedeng.io/api-documentation/

        if not self.indeed_api_key:
            return jobs

        for keyword in keywords:
            for location in locations:
                try:
                    url = "http://api.indeed.com/ads/apisearch"
                    params = {
                        'publisher': self.indeed_api_key,
                        'q': keyword,
                        'l': location,
                        'limit': 50,
                        'format': 'json',
                        'v': '2',
                    }

                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        for job in data.get('results', []):
                            jobs.append(self._parse_indeed_job(job))

                    time.sleep(0.5)

                except Exception as e:
                    print(f"Error fetching Indeed jobs: {e}")

        return jobs

    def fetch_greenhouse_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Greenhouse public job boards."""
        jobs = []

        # Expanded list of companies using Greenhouse
        # Greenhouse is one of the most popular ATS systems
        # This list includes tech companies, startups, and established businesses
        greenhouse_companies = [
            # Fintech
            'stripe', 'coinbase', 'plaid', 'chime', 'affirm', 'square', 'brex', 'ramp', 'mercury',
            'robinhood', 'carta', 'checkr', 'blend', 'marqeta', 'novi', 'checkout', 'adyen',

            # Tech Giants & Unicorns
            'airbnb', 'dropbox', 'pinterest', 'snap', 'reddit', 'discord', 'notion', 'databricks',

            # AI/ML Companies
            'anthropic', 'openai', 'scale', 'huggingface', 'cohere', 'jasper',

            # Developer Tools
            'gitlab', 'github', 'vercel', 'netlify', 'hashicorp', 'datadog', 'newrelic',
            'sentry', 'postman', 'docker', 'circleci', 'buildkite',

            # Design/Product
            'figma', 'canva', 'miro', 'invision', 'abstract', 'framer',

            # Productivity/Collaboration
            'airtable', 'webflow', 'amplitude', 'mixpanel', 'segment', 'heap', 'pendo',
            'monday', 'notion', 'coda', 'clickup',

            # HR/People
            'gusto', 'rippling', 'lattice', 'cultura', 'greenhouse', 'lever', 'workday',
            'zenefits', 'namely', 'justworks', 'trinet',

            # Healthcare/Biotech
            'oscar', 'devoted', 'crossover', 'cityblock', 'commure', 'benchling',
            'ginkgobioworks', 'recursion', 'insitro',

            # E-commerce/Retail
            'faire', 'whatnot', 'poshmark', 'depop', 'stockx', 'goat', 'rebag',

            # Autonomous/Hardware
            'nuro', 'cruise', 'zoox', 'aurora', 'embark', 'anduril', 'relativity',

            # Real Estate/PropTech
            'opendoor', 'zillow', 'redfin', 'compass', 'divvy', 'arrived',

            # Gaming/Entertainment
            'roblox', 'epic', 'riot', 'discord', 'twitch',

            # Crypto/Web3
            'coinbase', 'opensea', 'alchemy', 'paradigm', 'dapper', 'chainalysis',

            # Education
            'coursera', 'udacity', 'udemy', 'outschool', 'masterclass', '2u',

            # Food/Delivery
            'instacart', 'doordash', 'gopuff', 'getir', 'gorillas',

            # Travel/Mobility
            'lyft', 'lime', 'bird', 'hopper', 'outdoorsy',

            # Security/Infrastructure
            'cloudflare', 'akamai', 'fastly', 'crowdstrike', 'wiz', 'lacework',
        ]

        for company in greenhouse_companies:
            try:
                # Greenhouse public API (no auth required)
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('jobs', []):
                        # Filter by keywords
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_greenhouse_job(job, company))

                time.sleep(0.3)

            except Exception as e:
                # Skip companies that don't have public boards
                pass

        return jobs

    def fetch_lever_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Lever public job boards."""
        jobs = []

        # Expanded list of companies using Lever
        # Lever is popular with mid-size to large tech companies
        lever_companies = [
            # Tech Giants
            'netflix', 'shopify', 'atlassian', 'elastic', 'mongodb', 'confluent',

            # Mobility/Transportation
            'lyft', 'bird', 'lime', 'getaround', 'turo', 'waymo',

            # Food/Delivery
            'doordash', 'instacart', 'grubhub', 'gopuff', 'postmates', 'caviar',

            # Social/Communication
            'reddit', 'nextdoor', 'discord', 'bumble', 'hinge', 'match',

            # Developer Tools/Data
            'segment', 'datadog', 'elastic', 'pagerduty', 'launchdarkly', 'split',
            'amplitude', 'fullstory', 'logrocket',

            # Productivity/Collaboration
            'asana', 'notion', 'airtable', 'coda', 'miro', 'figma', 'linear',
            'clickup', 'height', 'superhuman',

            # Education/Learning
            'coursera', 'udacity', 'udemy', 'outschool', 'masterclass', 'skillshare',
            'pluralsight', 'teachable',

            # Events/Community
            'eventbrite', 'hopin', 'run-the-world', 'luma', 'partiful',

            # Finance/Banking
            'nubank', 'n26', 'revolut', 'monzo', 'current', 'dave',

            # Healthcare/Wellness
            'ro', 'hims', 'nurx', 'talkspace', 'betterhelp', 'headspace', 'calm',

            # E-commerce/Marketplaces
            'poshmark', 'mercari', 'offerup', 'reverb', 'chairish',

            # Real Estate
            'redfin', 'opendoor', 'homelight', 'knock', 'flyhomes',

            # Gaming
            'niantic', 'scopely', 'supercell', 'voodoo', 'playrix',

            # Media/Content
            'spotify', 'soundcloud', 'patreon', 'substack', 'medium',

            # Infrastructure/Cloud
            'digitalocean', 'linode', 'vultr', 'packet', 'equinix',

            # Security
            'snyk', 'teleport', 'detectify', 'bugcrowd', 'hackerone',
        ]

        for company in lever_companies:
            try:
                # Lever public API (no auth required)
                url = f"https://api.lever.co/v0/postings/{company}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data:
                        # Filter by keywords
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_lever_job(job, company))

                time.sleep(0.3)

            except Exception as e:
                # Skip companies that don't have public boards
                pass

        return jobs

    def fetch_workday_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Workday ATS public job boards."""
        jobs = []

        # Major companies using Workday
        workday_companies = [
            ('amazon', 'https://amazon.jobs/api/jobs'),
            ('apple', 'https://jobs.apple.com/api/role'),
            ('microsoft', 'https://careers.microsoft.com/professionals/us/en/search-results'),
            ('walmart', 'https://careers.walmart.com/api/jobs'),
            ('target', 'https://jobs.target.com/api/jobs'),
            ('mcdonalds', 'https://careers.mcdonalds.com/api/jobs'),
        ]

        for company_name, base_url in workday_companies:
            try:
                # Workday has a semi-standardized API structure
                # Most Workday sites follow similar patterns
                response = requests.get(base_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    # Parse response (structure varies by company)
                    pass

                time.sleep(0.5)

            except Exception as e:
                # Skip companies with different structures
                pass

        return jobs

    def fetch_icims_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from iCIMS ATS public job boards."""
        jobs = []

        # Major companies using iCIMS
        icims_companies = [
            ('uber', 'https://www.uber.com/api/loadSearchJobsResults'),
            ('walmart', 'https://careers.walmart.com'),
            ('pepsi', 'https://www.pepsicojobs.com'),
        ]

        for company_name, base_url in icims_companies:
            try:
                # iCIMS job board API
                response = requests.get(base_url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    # Parse iCIMS response
                    pass

                time.sleep(0.5)

            except Exception as e:
                pass

        return jobs

    def fetch_smartrecruiters_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from SmartRecruiters ATS public job boards."""
        jobs = []

        # SmartRecruiters has a public API
        # Format: https://api.smartrecruiters.com/v1/companies/{companyId}/postings

        smartrecruiters_companies = [
            'linkedin', 'bosch', 'visa', 'skechers', 'ikea',
        ]

        for company in smartrecruiters_companies:
            try:
                url = f"https://api.smartrecruiters.com/v1/companies/{company}/postings"
                params = {
                    'limit': 100,
                }
                response = requests.get(url, params=params, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('content', []):
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_smartrecruiters_job(job, company))

                time.sleep(0.3)

            except Exception as e:
                pass

        return jobs

    def fetch_workable_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Workable ATS public job boards."""
        jobs = []

        # Workable companies - public job boards at {company}.workable.com
        workable_companies = [
            'hubspot', 'zendesk', 'hootsuite', 'intercom', 'drift',
        ]

        for company in workable_companies:
            try:
                # Workable API endpoint
                url = f"https://apply.workable.com/api/v1/accounts/{company}/jobs"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('jobs', []):
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_workable_job(job, company))

                time.sleep(0.3)

            except Exception as e:
                pass

        return jobs

    def fetch_teamtailor_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Teamtailor ATS public job boards."""
        jobs = []

        # Teamtailor has a public API
        # Format: https://api.teamtailor.com/v1/jobs

        teamtailor_companies = [
            'spotify', 'klarna', 'northvolt', 'einride',
        ]

        for company in teamtailor_companies:
            try:
                url = f"https://api.teamtailor.com/v1/jobs"
                params = {
                    'filter[company]': company,
                    'page[size]': 50,
                }
                response = requests.get(url, params=params, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('data', []):
                        if self._matches_keywords(job.get('attributes', {}), keywords):
                            jobs.append(self._parse_teamtailor_job(job, company))

                time.sleep(0.3)

            except Exception as e:
                pass

        return jobs

    def fetch_bamboohr_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from BambooHR ATS public job boards."""
        jobs = []

        # BambooHR companies have public job boards
        # Format: {company}.bamboohr.com/jobs/

        bamboohr_companies = [
            'soundcloud', 'asana', 'foursquare',
        ]

        for company in bamboohr_companies:
            try:
                url = f"https://{company}.bamboohr.com/jobs/list/"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Parse BambooHR job listings
                    pass

                time.sleep(0.5)

            except Exception as e:
                pass

        return jobs

    def fetch_ashby_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Ashby ATS public job boards."""
        jobs = []

        # Ashby is a newer ATS with public job boards
        # Format: jobs.ashbyhq.com/{company}

        ashby_companies = [
            'anthropic', 'scale', 'retool', 'ramp', 'vanta',
        ]

        for company in ashby_companies:
            try:
                url = f"https://jobs.ashbyhq.com/{company}/jobs"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    # Try to parse JSON API if available
                    try:
                        data = response.json()
                        for job in data.get('jobs', []):
                            if self._matches_keywords(job, keywords):
                                jobs.append(self._parse_ashby_job(job, company))
                    except:
                        # Otherwise parse HTML
                        soup = BeautifulSoup(response.text, 'html.parser')
                        pass

                time.sleep(0.5)

            except Exception as e:
                pass

        return jobs

    def fetch_breezyhr_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Breezy HR ATS public job boards."""
        jobs = []

        # Breezy HR companies
        # Format: {company}.breezy.hr

        breezyhr_companies = [
            'clearbit', 'segment', 'mattermost',
        ]

        for company in breezyhr_companies:
            try:
                url = f"https://{company}.breezy.hr/json"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data:
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_breezyhr_job(job, company))

                time.sleep(0.5)

            except Exception as e:
                pass

        return jobs

    def fetch_glassdoor_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Glassdoor."""
        jobs = []

        # Glassdoor scraping - note this may be fragile due to site structure changes
        for keyword in keywords[:2]:  # Limit to avoid too many requests
            try:
                search_term = keyword.replace(' ', '+')
                url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_term}"

                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Glassdoor uses various class names, try multiple selectors
                    job_cards = soup.find_all(['li', 'div'], class_=lambda x: x and ('job' in str(x).lower() or 'listing' in str(x).lower()))

                    for card in job_cards[:30]:
                        try:
                            title_elem = card.find(['a', 'h2'], class_=lambda x: x and 'job' in str(x).lower())
                            title = title_elem.get_text(strip=True) if title_elem else ''

                            if title:
                                company_elem = card.find(['span', 'div'], class_=lambda x: x and 'employer' in str(x).lower())
                                if not company_elem:
                                    company_elem = card.find(['span', 'div'], class_=lambda x: x and 'company' in str(x).lower())
                                company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                                location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                                location = location_elem.get_text(strip=True) if location_elem else ''

                                url_elem = card.find('a', href=True)
                                job_url = url_elem['href'] if url_elem else ''
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://www.glassdoor.com{job_url}"

                                jobs.append({
                                    'external_id': f"glassdoor_{hash(job_url)}",
                                    'source': 'glassdoor',
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': '',
                                    'url': job_url,
                                    'posted_date': datetime.utcnow(),
                                })
                        except Exception:
                            continue

                time.sleep(2)  # Respectful rate limiting

            except Exception as e:
                print(f"Error fetching Glassdoor jobs: {e}")

        return jobs

    def fetch_builtin_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Built In job boards."""
        jobs = []

        # Built In has location-specific sites and a general product page
        try:
            url = "https://builtin.com/jobs/product"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Built In uses structured job cards
                job_cards = soup.find_all(['div', 'article'], class_=lambda x: x and 'job' in str(x).lower())

                for card in job_cards[:50]:
                    try:
                        title_elem = card.find(['h2', 'h3', 'a'], class_=lambda x: x and ('title' in str(x).lower() or 'job' in str(x).lower()))
                        title = title_elem.get_text(strip=True) if title_elem else ''

                        if title and self._matches_keywords({'title': title}, keywords):
                            company_elem = card.find(['span', 'div', 'a'], class_=lambda x: x and 'company' in str(x).lower())
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                            location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                            location = location_elem.get_text(strip=True) if location_elem else ''

                            url_elem = card.find('a', href=True)
                            job_url = url_elem['href'] if url_elem else ''
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://builtin.com{job_url}"

                            jobs.append({
                                'external_id': f"builtin_{hash(job_url)}",
                                'source': 'builtin',
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'url': job_url,
                                'posted_date': datetime.utcnow(),
                            })
                    except Exception:
                        continue

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching Built In jobs: {e}")

        return jobs

    def fetch_wellfound_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Wellfound (AngelList Talent)."""
        jobs = []

        # Wellfound has a GraphQL API
        # https://wellfound.com/graphql

        if not self.wellfound_api_key:
            return jobs

        try:
            # Wellfound API endpoint
            url = "https://wellfound.com/graphql"

            for keyword in keywords[:2]:
                query = """
                query JobSearch($slug: String!, $role: String) {
                  jobs(slug: $slug, role: $role) {
                    id
                    title
                    company {
                      name
                    }
                    locationNames
                    description
                    url
                  }
                }
                """

                variables = {
                    "slug": "product-manager",
                    "role": keyword
                }

                response = requests.post(
                    url,
                    json={"query": query, "variables": variables},
                    headers={**self.headers, 'Authorization': f'Bearer {self.wellfound_api_key}'},
                    timeout=10
                )

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('data', {}).get('jobs', []):
                        jobs.append(self._parse_wellfound_job(job))

                time.sleep(1)

        except Exception as e:
            print(f"Error fetching Wellfound jobs: {e}")

        return jobs

    def fetch_yc_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Y Combinator Work at a Startup."""
        jobs = []

        try:
            # YC jobs page for product managers
            url = "https://www.ycombinator.com/jobs/role/product-manager"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # YC uses structured job listings
                job_cards = soup.find_all(['div', 'a'], class_=lambda x: x and 'job' in str(x).lower())
                if not job_cards:
                    # Try alternative selector
                    job_cards = soup.find_all(['div', 'article'])

                for card in job_cards[:50]:
                    try:
                        # Look for title
                        title_elem = card.find(['h3', 'h2', 'span'], class_=lambda x: x and ('title' in str(x).lower() or 'position' in str(x).lower()))
                        if not title_elem:
                            title_elem = card.find(['h3', 'h2'])
                        title = title_elem.get_text(strip=True) if title_elem else ''

                        if title and self._matches_keywords({'title': title}, keywords):
                            company_elem = card.find(['span', 'div', 'a'], class_=lambda x: x and 'company' in str(x).lower())
                            company = company_elem.get_text(strip=True) if company_elem else 'YC Company'

                            location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                            location = location_elem.get_text(strip=True) if location_elem else ''

                            url_elem = card.find('a', href=True)
                            job_url = url_elem['href'] if url_elem else ''
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://www.ycombinator.com{job_url}"

                            jobs.append({
                                'external_id': f"yc_{hash(job_url)}",
                                'source': 'yc_jobs',
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'url': job_url,
                                'posted_date': datetime.utcnow(),
                            })
                    except Exception:
                        continue

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching YC jobs: {e}")

        return jobs

    def fetch_remoteok_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Remote OK."""
        jobs = []

        try:
            # Remote OK has a public API
            # https://remoteok.com/api
            url = "https://remoteok.com/api"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # First item is metadata, skip it
                for job in data[1:]:
                    # Filter by keywords
                    if self._matches_keywords(job, keywords):
                        jobs.append(self._parse_remoteok_job(job))

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching Remote OK jobs: {e}")

        return jobs

    def fetch_weworkremotely_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from We Work Remotely RSS feed."""
        jobs = []

        try:
            # We Work Remotely RSS feed
            url = "https://weworkremotely.com/categories/remote-product-jobs.rss"
            feed = feedparser.parse(url)

            for entry in feed.entries:
                jobs.append({
                    'external_id': f"wwr_{entry.get('id', '')}",
                    'source': 'weworkremotely',
                    'title': entry.get('title', ''),
                    'company': self._extract_company_from_title(entry.get('title', '')),
                    'location': 'Remote',
                    'description': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'posted_date': self._parse_rss_date(entry.get('published')),
                })

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching We Work Remotely jobs: {e}")

        return jobs

    def fetch_mindtheproduct_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Mind the Product job board."""
        jobs = []

        try:
            url = "https://www.mindtheproduct.com/jobs/"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Mind the Product is a WordPress-based job board
                # Look for job listings in common WordPress job board structures
                job_cards = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and ('job' in str(x).lower() or 'listing' in str(x).lower()))

                for card in job_cards[:50]:
                    try:
                        title_elem = card.find(['h2', 'h3', 'h4', 'a'], class_=lambda x: not x or 'title' in str(x).lower() or 'job' in str(x).lower())
                        if not title_elem:
                            title_elem = card.find(['h2', 'h3', 'h4'])
                        title = title_elem.get_text(strip=True) if title_elem else ''

                        if title and self._matches_keywords({'title': title}, keywords):
                            company_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'company' in str(x).lower())
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                            location_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'location' in str(x).lower())
                            location = location_elem.get_text(strip=True) if location_elem else ''

                            url_elem = card.find('a', href=True)
                            job_url = url_elem['href'] if url_elem else ''
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://www.mindtheproduct.com{job_url}"

                            jobs.append({
                                'external_id': f"mindtheproduct_{hash(job_url)}",
                                'source': 'mindtheproduct',
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'url': job_url,
                                'posted_date': datetime.utcnow(),
                            })
                    except Exception:
                        continue

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching Mind the Product jobs: {e}")

        return jobs

    def fetch_otta_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Otta."""
        jobs = []

        try:
            # Otta has a public job search page we can scrape
            for keyword in keywords[:2]:
                url = f"https://otta.com/jobs?q={keyword.replace(' ', '+')}"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Otta uses React-based UI, try to find job cards
                    job_cards = soup.find_all(['div', 'article'], attrs={'data-test': lambda x: x and 'job' in str(x).lower()})
                    if not job_cards:
                        job_cards = soup.find_all(['div', 'a'], class_=lambda x: x and 'job' in str(x).lower())

                    for card in job_cards[:50]:
                        try:
                            title_elem = card.find(['h2', 'h3', 'span'])
                            title = title_elem.get_text(strip=True) if title_elem else ''

                            if title and self._matches_keywords({'title': title}, keywords):
                                company_elem = card.find(['span', 'div'], class_=lambda x: x and 'company' in str(x).lower())
                                company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                                location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                                location = location_elem.get_text(strip=True) if location_elem else ''

                                url_elem = card.find('a', href=True)
                                job_url = url_elem['href'] if url_elem else ''
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://otta.com{job_url}"

                                jobs.append({
                                    'external_id': f"otta_{hash(job_url)}",
                                    'source': 'otta',
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': '',
                                    'url': job_url,
                                    'posted_date': datetime.utcnow(),
                                })
                        except Exception:
                            continue

                time.sleep(2)

        except Exception as e:
            print(f"Error fetching Otta jobs: {e}")

        return jobs

    def fetch_dice_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Dice."""
        jobs = []

        try:
            # Dice has a search API
            for keyword in keywords[:2]:
                url = f"https://www.dice.com/jobs?q={keyword.replace(' ', '+')}"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Parse Dice job listings

                time.sleep(2)

        except Exception as e:
            print(f"Error fetching Dice jobs: {e}")

        return jobs

    def fetch_welcometothejungle_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Welcome to the Jungle."""
        jobs = []

        try:
            # Welcome to the Jungle has a public job search API
            # They have location-specific sites (US, UK, FR, etc.)
            # US site: https://www.welcometothejungle.com/en/jobs

            for keyword in keywords[:2]:
                # Welcome to the Jungle API endpoint
                url = "https://www.welcometothejungle.com/api/v1/jobs"
                params = {
                    'query': keyword,
                    'page': 1,
                    'per_page': 50,
                }

                response = requests.get(url, params=params, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    for job in data.get('jobs', []):
                        # Filter by keywords to ensure relevance
                        if self._matches_keywords(job, keywords):
                            jobs.append(self._parse_welcometothejungle_job(job))

                time.sleep(2)

        except Exception as e:
            print(f"Error fetching Welcome to the Jungle jobs: {e}")

        return jobs

    def fetch_productjobs_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from ProductJobs.com."""
        jobs = []

        try:
            # ProductJobs is a product management job board
            # Try both web scraping and RSS feed approaches
            url = "https://productjobs.com/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse job listings - ProductJobs typically uses structured HTML
                job_cards = soup.find_all(['div', 'article'], class_=lambda x: x and ('job' in str(x).lower() or 'position' in str(x).lower()))

                for card in job_cards[:50]:  # Limit to first 50
                    try:
                        # Extract job details from card structure
                        title_elem = card.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in str(x).lower())
                        title = title_elem.get_text(strip=True) if title_elem else ''

                        # Check if matches keywords
                        if title and any(keyword.lower() in title.lower() for keyword in keywords):
                            company_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'company' in str(x).lower())
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                            location_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'location' in str(x).lower())
                            location = location_elem.get_text(strip=True) if location_elem else 'Remote'

                            url_elem = card.find('a', href=True)
                            job_url = url_elem['href'] if url_elem else ''
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://productjobs.com{job_url}"

                            jobs.append({
                                'external_id': f"productjobs_{hash(job_url)}",
                                'source': 'productjobs',
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'url': job_url,
                                'posted_date': datetime.utcnow(),
                            })
                    except Exception:
                        continue

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching ProductJobs jobs: {e}")

        return jobs

    def fetch_trueup_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from TrueUp.io."""
        jobs = []

        try:
            # TrueUp is a tech startup job board with compensation data
            # They have a public job search page
            for keyword in keywords[:2]:
                url = f"https://www.trueup.io/jobs?q={keyword.replace(' ', '+')}"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Parse job cards from TrueUp
                    job_cards = soup.find_all(['div', 'article'], attrs={'data-job': True})
                    if not job_cards:
                        job_cards = soup.find_all(['div', 'li'], class_=lambda x: x and 'job' in str(x).lower())

                    for card in job_cards[:50]:
                        try:
                            # Extract job info
                            title_elem = card.find(['h2', 'h3', 'a'])
                            title = title_elem.get_text(strip=True) if title_elem else ''

                            if title and self._matches_keywords({'title': title}, keywords):
                                company_elem = card.find(['span', 'div'], class_=lambda x: x and 'company' in str(x).lower())
                                company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                                location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                                location = location_elem.get_text(strip=True) if location_elem else 'Remote'

                                url_elem = card.find('a', href=True)
                                job_url = url_elem['href'] if url_elem else ''
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://www.trueup.io{job_url}"

                                jobs.append({
                                    'external_id': f"trueup_{hash(job_url)}",
                                    'source': 'trueup',
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': '',
                                    'url': job_url,
                                    'posted_date': datetime.utcnow(),
                                })
                        except Exception:
                            continue

                time.sleep(2)

        except Exception as e:
            print(f"Error fetching TrueUp jobs: {e}")

        return jobs

    def fetch_pave_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Pave."""
        jobs = []

        try:
            # Pave is primarily a compensation data platform
            # Check if they have a public job board
            url = "https://www.pave.com/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Parse job listings if available
                job_cards = soup.find_all(['div', 'li'], class_=lambda x: x and 'job' in str(x).lower())

                for card in job_cards[:50]:
                    try:
                        title_elem = card.find(['h2', 'h3', 'h4', 'a'])
                        title = title_elem.get_text(strip=True) if title_elem else ''

                        if title and self._matches_keywords({'title': title}, keywords):
                            company_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'company' in str(x).lower())
                            company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                            location_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
                            location = location_elem.get_text(strip=True) if location_elem else 'Remote'

                            url_elem = card.find('a', href=True)
                            job_url = url_elem['href'] if url_elem else ''
                            if job_url and not job_url.startswith('http'):
                                job_url = f"https://www.pave.com{job_url}"

                            jobs.append({
                                'external_id': f"pave_{hash(job_url)}",
                                'source': 'pave',
                                'title': title,
                                'company': company,
                                'location': location,
                                'description': '',
                                'url': job_url,
                                'posted_date': datetime.utcnow(),
                            })
                    except Exception:
                        continue

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching Pave jobs: {e}")

        return jobs

    def fetch_hiringcafe_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Hiring Cafe."""
        jobs = []

        try:
            # Hiring Cafe is a curated job board for tech roles
            # They have a simple job board interface
            for keyword in keywords[:2]:
                url = f"https://hiring.cafe/search?q={keyword.replace(' ', '+')}"
                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Hiring Cafe uses structured job listings
                    job_cards = soup.find_all(['div', 'article', 'li'], class_=lambda x: x and 'job' in str(x).lower())
                    if not job_cards:
                        # Try alternative selectors
                        job_cards = soup.find_all(['div', 'article'], attrs={'data-job-id': True})
                    if not job_cards:
                        job_cards = soup.find_all(['a'], href=lambda x: x and '/job/' in str(x))

                    for card in job_cards[:50]:
                        try:
                            # Extract job title
                            title_elem = card.find(['h2', 'h3', 'h4', 'span'], class_=lambda x: x and 'title' in str(x).lower())
                            if not title_elem:
                                title_elem = card.find(['h2', 'h3', 'h4'])
                            title = title_elem.get_text(strip=True) if title_elem else ''

                            if title and self._matches_keywords({'title': title}, keywords):
                                # Extract company
                                company_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'company' in str(x).lower())
                                company = company_elem.get_text(strip=True) if company_elem else 'Unknown'

                                # Extract location
                                location_elem = card.find(['span', 'div', 'p'], class_=lambda x: x and 'location' in str(x).lower())
                                location = location_elem.get_text(strip=True) if location_elem else 'Remote'

                                # Extract URL
                                url_elem = card.find('a', href=True)
                                if not url_elem and card.name == 'a':
                                    url_elem = card
                                job_url = url_elem['href'] if url_elem else ''
                                if job_url and not job_url.startswith('http'):
                                    job_url = f"https://hiring.cafe{job_url}"

                                jobs.append({
                                    'external_id': f"hiringcafe_{hash(job_url)}",
                                    'source': 'hiringcafe',
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': '',
                                    'url': job_url,
                                    'posted_date': datetime.utcnow(),
                                })
                        except Exception:
                            continue

                time.sleep(2)

        except Exception as e:
            print(f"Error fetching Hiring Cafe jobs: {e}")

        return jobs

    # Parser methods

    def _parse_linkedin_job(self, job: Dict) -> Dict:
        """Parse LinkedIn API job response."""
        return {
            'external_id': str(job.get('id', '')),
            'source': 'linkedin',
            'title': job.get('title', ''),
            'company': job.get('companyName', ''),
            'location': job.get('location', ''),
            'description': job.get('description', ''),
            'url': job.get('url', ''),
            'posted_date': self._parse_date(job.get('listedAt')),
            'job_type': job.get('employmentType', ''),
        }

    def _parse_indeed_job(self, job: Dict) -> Dict:
        """Parse Indeed API job response."""
        return {
            'external_id': job.get('jobkey', ''),
            'source': 'indeed',
            'title': job.get('jobtitle', ''),
            'company': job.get('company', ''),
            'location': job.get('formattedLocation', ''),
            'description': job.get('snippet', ''),
            'url': job.get('url', ''),
            'posted_date': self._parse_date(job.get('date')),
        }

    def _parse_greenhouse_job(self, job: Dict, company: str) -> Dict:
        """Parse Greenhouse job response."""
        return {
            'external_id': f"greenhouse_{job.get('id', '')}",
            'source': 'greenhouse',
            'title': job.get('title', ''),
            'company': company,
            'location': job.get('location', {}).get('name', ''),
            'description': job.get('content', ''),
            'url': job.get('absolute_url', ''),
            'posted_date': self._parse_date(job.get('updated_at')),
        }

    def _parse_lever_job(self, job: Dict, company: str) -> Dict:
        """Parse Lever job response."""
        return {
            'external_id': f"lever_{job.get('id', '')}",
            'source': 'lever',
            'title': job.get('text', ''),
            'company': company,
            'location': job.get('categories', {}).get('location', ''),
            'description': job.get('description', ''),
            'url': job.get('hostedUrl', ''),
            'posted_date': self._parse_date(job.get('createdAt')),
        }

    def _parse_wellfound_job(self, job: Dict) -> Dict:
        """Parse Wellfound API job response."""
        return {
            'external_id': f"wellfound_{job.get('id', '')}",
            'source': 'wellfound',
            'title': job.get('title', ''),
            'company': job.get('company', {}).get('name', ''),
            'location': ', '.join(job.get('locationNames', [])),
            'description': job.get('description', ''),
            'url': job.get('url', ''),
            'posted_date': datetime.utcnow(),
        }

    def _parse_remoteok_job(self, job: Dict) -> Dict:
        """Parse Remote OK API job response."""
        return {
            'external_id': f"remoteok_{job.get('id', '')}",
            'source': 'remoteok',
            'title': job.get('position', ''),
            'company': job.get('company', ''),
            'location': 'Remote',
            'description': job.get('description', ''),
            'url': job.get('url', ''),
            'posted_date': self._parse_date(job.get('date')),
        }

    def _parse_welcometothejungle_job(self, job: Dict) -> Dict:
        """Parse Welcome to the Jungle API job response."""
        return {
            'external_id': f"wttj_{job.get('id', '')}",
            'source': 'welcometothejungle',
            'title': job.get('name', ''),
            'company': job.get('organization', {}).get('name', ''),
            'location': job.get('office', {}).get('city', 'Remote'),
            'description': job.get('description', ''),
            'url': f"https://www.welcometothejungle.com/en/companies/{job.get('organization', {}).get('slug', '')}/jobs/{job.get('slug', '')}",
            'posted_date': self._parse_date(job.get('published_at')),
        }

    def _parse_smartrecruiters_job(self, job: Dict, company: str) -> Dict:
        """Parse SmartRecruiters API job response."""
        return {
            'external_id': f"smartrecruiters_{job.get('id', '')}",
            'source': 'smartrecruiters',
            'title': job.get('name', ''),
            'company': company,
            'location': job.get('location', {}).get('city', ''),
            'description': job.get('description', ''),
            'url': f"https://jobs.smartrecruiters.com/{company}/{job.get('id', '')}",
            'posted_date': self._parse_date(job.get('releasedDate')),
        }

    def _parse_workable_job(self, job: Dict, company: str) -> Dict:
        """Parse Workable API job response."""
        return {
            'external_id': f"workable_{job.get('shortcode', '')}",
            'source': 'workable',
            'title': job.get('title', ''),
            'company': company,
            'location': job.get('location', {}).get('city', ''),
            'description': job.get('description', ''),
            'url': f"https://apply.workable.com/{company}/j/{job.get('shortcode', '')}",
            'posted_date': self._parse_date(job.get('published_on')),
        }

    def _parse_teamtailor_job(self, job: Dict, company: str) -> Dict:
        """Parse Teamtailor API job response."""
        attributes = job.get('attributes', {})
        return {
            'external_id': f"teamtailor_{job.get('id', '')}",
            'source': 'teamtailor',
            'title': attributes.get('title', ''),
            'company': company,
            'location': attributes.get('location', ''),
            'description': attributes.get('body', ''),
            'url': attributes.get('apply_url', ''),
            'posted_date': self._parse_date(attributes.get('created_at')),
        }

    def _parse_ashby_job(self, job: Dict, company: str) -> Dict:
        """Parse Ashby API job response."""
        return {
            'external_id': f"ashby_{job.get('id', '')}",
            'source': 'ashby',
            'title': job.get('title', ''),
            'company': company,
            'location': job.get('location', ''),
            'description': job.get('description', ''),
            'url': f"https://jobs.ashbyhq.com/{company}/{job.get('id', '')}",
            'posted_date': self._parse_date(job.get('publishedAt')),
        }

    def _parse_breezyhr_job(self, job: Dict, company: str) -> Dict:
        """Parse Breezy HR API job response."""
        return {
            'external_id': f"breezyhr_{job.get('_id', '')}",
            'source': 'breezyhr',
            'title': job.get('name', ''),
            'company': company,
            'location': job.get('location', {}).get('name', ''),
            'description': job.get('description', ''),
            'url': f"https://{company}.breezy.hr/p/{job.get('friendly_id', '')}",
            'posted_date': self._parse_date(job.get('published_date')),
        }

    # Helper methods

    def _matches_keywords(self, job: Dict, keywords: List[str]) -> bool:
        """Check if job matches any of the keywords."""
        job_text = (
            str(job.get('title', '')) + ' ' +
            str(job.get('text', '')) + ' ' +
            str(job.get('description', ''))
        ).lower()

        return any(keyword.lower() in job_text for keyword in keywords)

    def _extract_company_from_title(self, title: str) -> str:
        """Extract company name from job title (used for RSS feeds)."""
        # Many RSS feeds format titles as "Company: Job Title"
        if ':' in title:
            return title.split(':')[0].strip()
        return 'Unknown'

    def _parse_date(self, date_str) -> datetime:
        """Parse date from various formats."""
        if not date_str:
            return datetime.utcnow()

        try:
            # Try ISO format
            if isinstance(date_str, str):
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            elif isinstance(date_str, int):
                # Unix timestamp
                return datetime.fromtimestamp(date_str / 1000)
        except Exception:
            pass

        return datetime.utcnow()

    def _parse_rss_date(self, date_str: str) -> datetime:
        """Parse RSS date format."""
        if not date_str:
            return datetime.utcnow()

        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return datetime.utcnow()

    def _deduplicate_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Remove duplicate jobs based on title and company."""
        seen = set()
        unique_jobs = []

        for job in jobs:
            key = (
                job.get('title', '').lower().strip(),
                job.get('company', '').lower().strip()
            )

            if key not in seen:
                seen.add(key)
                unique_jobs.append(job)

        return unique_jobs
