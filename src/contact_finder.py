"""Contact finder service to identify hiring managers and recruiters."""

import os
import re
from typing import List, Dict, Optional
from anthropic import Anthropic


class ContactFinder:
    """Find hiring managers, recruiters, and guess email addresses."""

    def __init__(self):
        """Initialize contact finder."""
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = 'claude-3-haiku-20240307'

        # Common email patterns
        self.email_patterns = [
            '{first}.{last}@{domain}',
            '{first}{last}@{domain}',
            '{first_initial}{last}@{domain}',
            '{first}_{last}@{domain}',
            '{first}-{last}@{domain}',
            '{last}.{first}@{domain}',
        ]

    def find_contacts_for_job(self, job: Dict, company_info: Dict = None) -> List[Dict]:
        """
        Find potential contacts for a job posting.

        Returns list of contacts with:
        - name
        - title
        - linkedin_url (estimated)
        - email (guessed based on patterns)
        - confidence (high/medium/low)
        - reasoning
        """
        contacts = []

        company_name = job.get('company', '')
        job_title = job.get('title', '')

        if not company_name:
            return contacts

        # Generate contact suggestions using AI
        ai_contacts = self._generate_contact_suggestions(company_name, job_title, company_info)

        for contact in ai_contacts:
            # Guess email address
            emails = self._guess_email_addresses(
                contact.get('name', ''),
                company_name,
                company_info
            )

            contact['email_guesses'] = emails
            contact['primary_email'] = emails[0] if emails else None

            # Generate LinkedIn search URL
            contact['linkedin_search_url'] = self._generate_linkedin_search_url(
                contact.get('name', ''),
                company_name,
                contact.get('title', '')
            )

            contacts.append(contact)

        return contacts

    def _generate_contact_suggestions(self, company: str, job_title: str, company_info: Dict = None) -> List[Dict]:
        """Use AI to suggest relevant contacts."""
        company_context = ""
        if company_info:
            company_context = f"""
Company information:
- Size: {company_info.get('size', 'Unknown')}
- Industry: {company_info.get('industry', 'Unknown')}
- Description: {company_info.get('description', '')}
"""

        prompt = f"""You are a recruiting assistant helping identify key contacts for a job application.

Job: {job_title}
Company: {company}
{company_context}

Generate a list of 3-5 people who would be valuable contacts for this job application.
Include:
1. Hiring manager(s) - who would directly manage this role
2. Recruiter(s) - who might be handling recruitment
3. Team members - people in similar roles
4. Senior leaders - relevant VPs or Directors

For each person, provide:
- Likely title/role
- Why they're relevant
- Confidence level (high/medium/low)

Format your response as JSON:
[
  {{
    "title": "VP of Product",
    "reasoning": "Would likely be hiring manager or decision maker for this senior PM role",
    "confidence": "high"
  }},
  ...
]

IMPORTANT: Only provide the JSON array, no other text."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse JSON response
            import json
            contacts_json = response.content[0].text.strip()

            # Remove markdown code blocks if present
            contacts_json = re.sub(r'```json\n?', '', contacts_json)
            contacts_json = re.sub(r'```\n?', '', contacts_json)

            contacts = json.loads(contacts_json)
            return contacts

        except Exception as e:
            print(f"Error generating contact suggestions: {e}")
            return []

    def _guess_email_addresses(self, name: str, company: str, company_info: Dict = None) -> List[str]:
        """Guess possible email addresses based on name and company."""
        if not name or not company:
            return []

        # Clean up name
        name_parts = name.lower().strip().split()
        if len(name_parts) < 2:
            return []

        first_name = name_parts[0]
        last_name = name_parts[-1]
        first_initial = first_name[0]

        # Get company domain
        domain = self._guess_company_domain(company, company_info)
        if not domain:
            return []

        # Generate email variations
        emails = []
        for pattern in self.email_patterns:
            email = pattern.format(
                first=first_name,
                last=last_name,
                first_initial=first_initial,
                domain=domain
            )
            emails.append(email)

        return emails

    def _guess_company_domain(self, company: str, company_info: Dict = None) -> Optional[str]:
        """Guess company email domain."""
        # Check if we have it from company info
        if company_info and company_info.get('domain'):
            return company_info['domain']

        # Clean company name
        company_clean = company.lower().strip()

        # Remove common suffixes
        company_clean = re.sub(r'\s+(inc|llc|ltd|corp|corporation|company|co)\s*$', '', company_clean)
        company_clean = re.sub(r'[^a-z0-9]', '', company_clean)

        # Common domain patterns
        return f"{company_clean}.com"

    def _generate_linkedin_search_url(self, name: str, company: str, title: str = "") -> str:
        """Generate LinkedIn search URL for finding the contact."""
        # Encode search parameters
        from urllib.parse import quote

        if name:
            # Search by name and company
            search_query = f"{name} {company}"
        else:
            # Search by title and company
            search_query = f"{title} {company}"

        encoded_query = quote(search_query)
        return f"https://www.linkedin.com/search/results/people/?keywords={encoded_query}"

    def generate_outreach_message(self, contact: Dict, job: Dict, user_profile: Dict) -> str:
        """Generate a personalized outreach message for a contact."""
        prompt = f"""Generate a brief, professional LinkedIn connection request message.

Contact: {contact.get('title', 'Professional')}
Company: {job.get('company', '')}
Job: {job.get('title', '')}

Your background:
- Current role: {user_profile.get('current_role', '')}
- Experience: {user_profile.get('years_experience', '')} years
- Top skills: {', '.join(user_profile.get('skills', [])[:3])}

Write a 200-character (max) connection request that:
1. Mentions the specific role you're interested in
2. Briefly states your relevant experience
3. Asks for a conversation
4. Is warm but professional

IMPORTANT: Keep it under 200 characters (LinkedIn limit)."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=256,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            message = response.content[0].text.strip()

            # Truncate if needed
            if len(message) > 200:
                message = message[:197] + "..."

            return message

        except Exception as e:
            print(f"Error generating outreach message: {e}")
            return ""

    def generate_cold_email(self, contact: Dict, job: Dict, user_profile: Dict) -> str:
        """Generate a cold email to the contact."""
        prompt = f"""Generate a professional cold email for a job application.

To: {contact.get('title', 'Hiring Manager')} at {job.get('company', '')}
Regarding: {job.get('title', '')} position

Your background:
- Current role: {user_profile.get('current_role', '')}
- Experience: {user_profile.get('years_experience', '')} years
- Top skills: {', '.join(user_profile.get('skills', [])[:5])}

Write a cold email (300 words max) that:
1. Subject line (under 50 characters)
2. Brief introduction
3. Why you're interested in the role
4. 2-3 relevant accomplishments
5. Call to action (request for conversation)

Format:
Subject: [subject line]

[email body]"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Error generating cold email: {e}")
            return ""


def test_contact_finder():
    """Test the contact finder."""
    finder = ContactFinder()

    test_job = {
        'title': 'Senior Product Manager',
        'company': 'Stripe',
        'description': 'We are looking for a senior PM to lead our payments platform...'
    }

    test_company = {
        'size': '5000+ employees',
        'industry': 'Financial Technology',
        'domain': 'stripe.com'
    }

    test_user = {
        'current_role': 'Product Manager',
        'years_experience': 8,
        'skills': ['Product Strategy', 'Data Analysis', 'A/B Testing', 'API Design']
    }

    print("Finding contacts for job...")
    contacts = finder.find_contacts_for_job(test_job, test_company)

    for i, contact in enumerate(contacts, 1):
        print(f"\n{i}. {contact.get('title', 'Unknown')}")
        print(f"   Reasoning: {contact.get('reasoning', '')}")
        print(f"   Confidence: {contact.get('confidence', '')}")
        print(f"   Email guesses: {', '.join(contact.get('email_guesses', [])[:3])}")
        print(f"   LinkedIn search: {contact.get('linkedin_search_url', '')}")

        # Generate outreach message
        message = finder.generate_outreach_message(contact, test_job, test_user)
        print(f"   Outreach: {message}")


if __name__ == '__main__':
    test_contact_finder()
