"""Company research module to gather insights and find contacts."""

import os
import time
from typing import Dict, List
import requests
from bs4 import BeautifulSoup


class CompanyResearcher:
    """Research companies and identify potential contacts."""

    def __init__(self):
        """Initialize company researcher."""
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY')

    def research_company(self, company_name: str, job_title: str) -> Dict:
        """
        Research a company and gather insights.

        Returns dict with:
        - company_info: basic info, funding, size
        - potential_contacts: list of people to connect with
        - insights: key data points to mention
        """
        print(f"Researching {company_name}...")

        company_info = {
            'name': company_name,
            'industry': None,
            'size': None,
            'funding_stage': None,
            'glassdoor_rating': None,
            'description': None,
        }

        # Get basic company info
        company_info.update(self._get_company_basics(company_name))

        # Find potential contacts
        potential_contacts = self._find_potential_contacts(company_name, job_title)

        # Generate insights
        insights = self._generate_insights(company_info, potential_contacts)

        return {
            'company_info': company_info,
            'potential_contacts': potential_contacts[:5],  # Top 5 contacts
            'insights': insights,
        }

    def _get_company_basics(self, company_name: str) -> Dict:
        """Get basic company information."""
        info = {}

        try:
            # Try to get LinkedIn company info
            # Note: This requires LinkedIn API access
            if self.linkedin_api_key:
                info.update(self._fetch_linkedin_company(company_name))

            # Could also integrate:
            # - Crunchbase API for funding data
            # - Glassdoor API for ratings
            # - Built In for tech stack
            # For now, we'll use public data where possible

        except Exception as e:
            print(f"Error fetching company basics: {e}")

        return info

    def _fetch_linkedin_company(self, company_name: str) -> Dict:
        """Fetch company info from LinkedIn API."""
        # This would use LinkedIn Company API
        # Requires LinkedIn API key with proper permissions

        # Placeholder - would implement actual API call
        return {
            'linkedin_url': f"https://www.linkedin.com/company/{company_name.lower().replace(' ', '-')}/",
        }

    def _find_potential_contacts(self, company_name: str, job_title: str) -> List[Dict]:
        """
        Identify potential contacts at the company.

        Returns list of contacts with:
        - name
        - title
        - linkedin_url
        - relevance_score
        - connection_reason
        """
        contacts = []

        # Potential contact types to look for (in order of priority):
        target_roles = [
            'VP Product', 'Director of Product', 'Head of Product',
            'Product Manager', 'Chief Product Officer', 'CPO',
            'Hiring Manager', 'Recruiter', 'Talent Acquisition',
            'Engineering Manager', 'CTO', 'CEO',
        ]

        # In a real implementation, this would:
        # 1. Use LinkedIn API to search for people at the company
        # 2. Filter by relevant roles
        # 3. Score by seniority and relevance to the job
        # 4. Generate personalized connection reasons

        # For now, we'll provide a template
        for i, role in enumerate(target_roles[:5]):
            contacts.append({
                'name': f"[Search LinkedIn for {role}]",
                'title': role,
                'linkedin_url': f"https://www.linkedin.com/search/results/people/?company={company_name.replace(' ', '%20')}&keywords={role.replace(' ', '%20')}",
                'relevance_score': 100 - (i * 10),
                'connection_reason': self._generate_connection_reason(role, job_title, company_name),
            })

        return contacts

    def _generate_connection_reason(self, contact_role: str, job_title: str, company_name: str) -> str:
        """Generate a reason why this contact is relevant."""
        reasons = {
            'VP Product': f"As VP Product at {company_name}, they would be directly involved in hiring for the {job_title} role and can provide insights into product strategy.",
            'Director of Product': f"Would likely be the hiring manager or close collaborator for the {job_title} position.",
            'Head of Product': f"Senior product leader who can share insights about product culture and team structure.",
            'Product Manager': f"Current PM who can provide on-the-ground perspective about working at {company_name}.",
            'CPO': f"Chief Product Officer who sets product vision and may be involved in senior hiring decisions.",
            'Hiring Manager': f"Direct hiring manager for open roles at {company_name}.",
            'Recruiter': f"Talent partner who can fast-track your application and provide interview tips.",
            'Talent Acquisition': f"Recruiting team member who can provide application guidance.",
            'Engineering Manager': f"Cross-functional partner who works closely with product team.",
            'CTO': f"Technical leader who can share insights about the engineering and product partnership.",
            'CEO': f"Company leader who can share vision and culture - valuable for senior roles.",
        }

        return reasons.get(contact_role, f"Relevant contact at {company_name} for the {job_title} role.")

    def _generate_insights(self, company_info: Dict, contacts: List[Dict]) -> List[str]:
        """Generate key insights about the company."""
        insights = []

        # Company size insights
        if company_info.get('size'):
            insights.append(f"Company size: {company_info['size']} employees")

        # Funding insights
        if company_info.get('funding_stage'):
            insights.append(f"Funding stage: {company_info['funding_stage']}")

        # Contact strategy
        if contacts:
            top_contact = contacts[0]
            insights.append(
                f"Best contact: Reach out to {top_contact['title']} - {top_contact['connection_reason']}"
            )

        # Industry insights
        if company_info.get('industry'):
            insights.append(f"Industry: {company_info['industry']}")

        return insights

    def generate_outreach_message(
        self,
        contact: Dict,
        job_title: str,
        company_name: str,
        user_profile: Dict
    ) -> str:
        """
        Generate a personalized LinkedIn connection message.

        Note: User will send this manually (we don't auto-send).
        """
        template = f"""Hi {contact.get('name', '[Name]')},

I noticed you're a {contact.get('title', 'product leader')} at {company_name}. I'm currently exploring the {job_title} opportunity there.

With 15 years of product leadership experience building AI-powered products at Realtor.com and CNBC, I'm excited about {company_name}'s mission.

Would love to connect and learn more about the product team and culture.

Best,
Jim Rome
"""

        return template.strip()

    def batch_research_companies(self, jobs: List[Dict]) -> Dict[str, Dict]:
        """Research multiple companies at once."""
        research_results = {}

        unique_companies = list(set([job.get('company') for job in jobs if job.get('company')]))

        for i, company in enumerate(unique_companies[:20], 1):  # Limit to 20 companies
            try:
                job_title = next(
                    (job.get('title') for job in jobs if job.get('company') == company),
                    'Product Manager'
                )

                research = self.research_company(company, job_title)
                research_results[company] = research

                print(f"✓ Researched {company} ({i}/{len(unique_companies[:20])})")

                time.sleep(0.5)  # Rate limiting

            except Exception as e:
                print(f"✗ Error researching {company}: {e}")

        return research_results
