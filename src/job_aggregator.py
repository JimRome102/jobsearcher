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
        greenhouse_companies = [
            'stripe', 'airbnb', 'robinhood', 'coinbase', 'plaid',
            'chime', 'affirm', 'square', 'datadog', 'notion',
            'gitlab', 'figma', 'amplitude', 'webflow', 'airtable',
            'gusto', 'rippling', 'brex', 'ramp', 'mercury',
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
        lever_companies = [
            'netflix', 'lyft', 'shopify', 'elastic', 'pagerduty',
            'reddit', 'segment', 'doordash', 'instacart', 'grubhub',
            'asana', 'atlassian', 'eventbrite', 'coursera', 'udacity',
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

    def fetch_glassdoor_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Glassdoor RSS feeds."""
        jobs = []

        # Glassdoor provides RSS feeds for job searches
        # Example: https://www.glassdoor.com/Job/jobs.htm?sc.keyword=product+manager

        for keyword in keywords[:2]:  # Limit to avoid too many requests
            try:
                # Glassdoor RSS feed format
                search_term = keyword.replace(' ', '+')
                url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={search_term}"

                response = requests.get(url, headers=self.headers, timeout=10)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Parse job cards from the page
                    # Note: Glassdoor structure may change, this is a basic implementation
                    # In production, consider using their official API if available

                time.sleep(2)  # Respectful rate limiting

            except Exception as e:
                print(f"Error fetching Glassdoor jobs: {e}")

        return jobs

    def fetch_builtin_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Built In job boards."""
        jobs = []

        # Built In has location-specific sites
        # https://builtin.com/jobs/product

        try:
            url = "https://builtin.com/jobs/product"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Parse job listings from Built In
                # Their site structure includes job cards with data attributes

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
            # YC jobs page
            url = "https://www.ycombinator.com/jobs/role/product-manager"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Parse YC job listings
                # YC has a structured job board with company data

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
                # Parse Mind the Product job listings
                # This is a WordPress-based job board

            time.sleep(2)

        except Exception as e:
            print(f"Error fetching Mind the Product jobs: {e}")

        return jobs

    def fetch_otta_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from Otta."""
        jobs = []

        try:
            # Otta requires authentication for their API
            # For now, skip unless API key is provided
            url = "https://otta.com/api/jobs"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Parse Otta jobs

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
