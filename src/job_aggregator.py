"""Job aggregation service to fetch jobs from multiple sources."""

import os
import time
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

    def fetch_all_jobs(self, keywords: List[str], locations: List[str]) -> List[Dict]:
        """Fetch jobs from all enabled sources."""
        all_jobs = []

        # Fetch from each source
        sources = {
            'linkedin': self.fetch_linkedin_jobs,
            'indeed': self.fetch_indeed_jobs,
            'greenhouse': self.fetch_greenhouse_jobs,
            'lever': self.fetch_lever_jobs,
        }

        for source_name, fetch_func in sources.items():
            try:
                jobs = fetch_func(keywords, locations)
                print(f"✓ Fetched {len(jobs)} jobs from {source_name}")
                all_jobs.extend(jobs)
                time.sleep(1)  # Rate limiting
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
            print("⚠ LinkedIn API key not found. Skipping LinkedIn jobs.")
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
            print("⚠ Indeed API key not found. Skipping Indeed jobs.")
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

        # Target companies known to use Greenhouse
        greenhouse_companies = [
            'stripe', 'airbnb', 'robinhood', 'coinbase', 'plaid',
            'chime', 'affirm', 'square', 'datadog', 'notion',
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

        # Target companies known to use Lever
        lever_companies = [
            'netflix', 'lyft', 'shopify', 'elastic', 'pagerduty',
            'reddit', 'segment', 'doordash', 'instacart',
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

    def _matches_keywords(self, job: Dict, keywords: List[str]) -> bool:
        """Check if job matches any of the keywords."""
        job_text = (
            str(job.get('title', '')) + ' ' +
            str(job.get('text', '')) + ' ' +
            str(job.get('description', ''))
        ).lower()

        return any(keyword.lower() in job_text for keyword in keywords)

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
