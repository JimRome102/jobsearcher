"""Resume parser to extract data from PDF resumes."""

import os
import re
from pathlib import Path
from typing import Dict, List
import PyPDF2
import pdfplumber


class ResumeParser:
    """Parse resumes and extract structured data."""

    def __init__(self, resume_directory: str):
        """Initialize parser with resume directory."""
        self.resume_directory = Path(resume_directory)

    def parse_all_resumes(self) -> Dict[str, Dict]:
        """Parse all PDF resumes in the directory."""
        resumes = {}

        # Find all PDF files
        pdf_files = list(self.resume_directory.rglob('*.pdf'))

        for pdf_path in pdf_files:
            # Skip non-resume PDFs (like case studies, licenses)
            if self._is_resume_file(pdf_path):
                try:
                    resume_data = self.parse_resume(str(pdf_path))
                    resumes[pdf_path.name] = resume_data
                    print(f"✓ Parsed: {pdf_path.name}")
                except Exception as e:
                    print(f"✗ Error parsing {pdf_path.name}: {e}")

        return resumes

    def _is_resume_file(self, pdf_path: Path) -> bool:
        """Check if PDF is likely a resume."""
        filename = pdf_path.name.lower()

        # Exclude case studies, licenses, etc.
        exclude_keywords = ['case study', 'license', 'help', 'mockup', 'cover letter']
        if any(keyword in filename for keyword in exclude_keywords):
            return False

        # Include files with "resume" or "cv" or company names for targeted resumes
        include_keywords = ['resume', 'cv', 'rome']
        if any(keyword in filename for keyword in include_keywords):
            return True

        return False

    def parse_resume(self, pdf_path: str) -> Dict:
        """Parse a single resume PDF."""
        text = self._extract_text(pdf_path)

        return {
            'file_path': pdf_path,
            'file_name': Path(pdf_path).name,
            'raw_text': text,
            'contact': self._extract_contact(text),
            'skills': self._extract_skills(text),
            'experience': self._extract_experience(text),
            'companies': self._extract_companies(text),
            'education': self._extract_education(text),
            'keywords': self._extract_keywords(text),
        }

    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF."""
        text = ""

        # Try pdfplumber first (better formatting)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception:
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

        return text

    def _extract_contact(self, text: str) -> Dict:
        """Extract contact information."""
        contact = {}

        # Email
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        email_match = re.search(email_pattern, text)
        if email_match:
            contact['email'] = email_match.group()

        # Phone
        phone_pattern = r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        phone_match = re.search(phone_pattern, text)
        if phone_match:
            contact['phone'] = phone_match.group()

        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_match = re.search(linkedin_pattern, text)
        if linkedin_match:
            contact['linkedin'] = linkedin_match.group()

        return contact

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills from resume."""
        skills = []

        # Common PM skills to look for
        skill_keywords = [
            'Product Management', 'Product Strategy', 'Agile', 'Scrum',
            'AI', 'Machine Learning', 'LLM', 'Generative AI',
            'Mobile App', 'iOS', 'Android', 'Web',
            'Data Analysis', 'A/B Testing', 'Experimentation',
            'User Experience', 'UX', 'UI',
            'SQL', 'Python', 'JavaScript',
            'Subscription', 'Monetization', 'Revenue Growth',
            'Search', 'Discovery', 'Personalization',
            'Fintech', 'Real Estate', 'B2C', 'Consumer',
            'Leadership', 'Cross-functional', 'Mentorship',
            'API', 'REST', 'AWS', 'Cloud',
        ]

        text_lower = text.lower()
        for skill in skill_keywords:
            if skill.lower() in text_lower:
                skills.append(skill)

        return list(set(skills))

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience."""
        experiences = []

        # Look for company names and roles
        # This is simplified - could be enhanced with NLP
        company_pattern = r'(Realtor\.com|CNBC|Consumer Reports|magicJack|WebMD|AT&T|Crisp Media|Universal McCann|MTV Networks)'
        companies = re.findall(company_pattern, text, re.IGNORECASE)

        for company in set(companies):
            experiences.append({'company': company})

        return experiences

    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names from experience."""
        companies = []
        company_pattern = r'(Realtor\.com|CNBC|NBCUniversal|Consumer Reports|magicJack|WebMD|AT&T|Crisp Media|Universal McCann|MTV Networks|Viacom)'
        found_companies = re.findall(company_pattern, text, re.IGNORECASE)

        return list(set(found_companies))

    def _extract_education(self, text: str) -> Dict:
        """Extract education information."""
        education = {}

        # Look for degree patterns
        degree_pattern = r'(B\.S\.|Bachelor|Master|MBA|Ph\.D\.)'
        degree_match = re.search(degree_pattern, text, re.IGNORECASE)
        if degree_match:
            education['degree'] = degree_match.group()

        # Look for university names
        university_pattern = r'(Indiana University|Cornell University|York University)'
        university_match = re.search(university_pattern, text, re.IGNORECASE)
        if university_match:
            education['university'] = university_match.group()

        return education

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords for matching."""
        keywords = []

        # High-value keywords for product management roles
        important_keywords = [
            # Role levels
            'Principal', 'Senior', 'Director', 'VP',

            # Technical
            'AI', 'LLM', 'Machine Learning', 'Generative AI',
            'iOS', 'Android', 'Mobile', 'Web',

            # Domains
            'Fintech', 'Finance', 'Real Estate', 'Consumer',
            'B2C', 'Subscription', 'Marketplace',

            # Outcomes
            'Revenue Growth', 'User Engagement', 'Retention',
            'A/B Testing', 'Experimentation',

            # Leadership
            'Cross-functional', 'Mentorship', 'Strategy',
        ]

        text_lower = text.lower()
        for keyword in important_keywords:
            if keyword.lower() in text_lower:
                keywords.append(keyword)

        return list(set(keywords))

    def get_resume_summary(self, resumes: Dict[str, Dict]) -> Dict:
        """Generate summary of all resumes."""
        all_skills = set()
        all_companies = set()
        all_keywords = set()

        for resume_data in resumes.values():
            all_skills.update(resume_data.get('skills', []))
            all_companies.update(resume_data.get('companies', []))
            all_keywords.update(resume_data.get('keywords', []))

        return {
            'total_resumes': len(resumes),
            'skills': sorted(list(all_skills)),
            'companies': sorted(list(all_companies)),
            'keywords': sorted(list(all_keywords)),
            'resume_files': list(resumes.keys()),
        }
