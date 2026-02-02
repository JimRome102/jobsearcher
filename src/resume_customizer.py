"""Resume customizer service to tailor resumes for specific jobs."""

import os
from pathlib import Path
from typing import Dict, List
from anthropic import Anthropic
from datetime import datetime


class ResumeCustomizer:
    """Customize resumes for specific job applications."""

    def __init__(self, resume_data: Dict, user_profile: Dict):
        """Initialize resume customizer."""
        self.resume_data = resume_data
        self.user_profile = user_profile
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        self.model = 'claude-3-haiku-20240307'

        # Output directory for customized resumes
        self.output_dir = Path(__file__).parent.parent / 'customized_resumes'
        self.output_dir.mkdir(exist_ok=True)

    def customize_resume_for_job(self, job: Dict) -> str:
        """
        Create a customized resume tailored to a specific job.

        Returns path to the generated resume file.
        """
        company = job.get('company', 'Company')
        title = job.get('title', 'Position')
        description = job.get('description', '')

        print(f"  Customizing resume for {title} at {company}...")

        # Generate customized resume content
        customized_content = self._generate_customized_resume(job)

        # Clean filename
        safe_company = self._sanitize_filename(company)
        safe_title = self._sanitize_filename(title)
        filename = f"Jim_Rome_Resume_{safe_company}_{safe_title}.txt"
        filepath = self.output_dir / filename

        # Save to file
        with open(filepath, 'w') as f:
            f.write(customized_content)

        return str(filepath)

    def _generate_customized_resume(self, job: Dict) -> str:
        """Use AI to generate a customized resume."""
        prompt = f"""You are an expert resume writer helping tailor a resume for a specific job application.

JOB POSTING:
Company: {job.get('company', '')}
Title: {job.get('title', '')}
Description: {job.get('description', '')}

CANDIDATE BACKGROUND:
Name: {self.user_profile.get('name', 'Jim Rome')}
Current Role: {self.user_profile.get('current_role', '')}
Years of Experience: {self.user_profile.get('years_experience', '')}
Skills: {', '.join(self.user_profile.get('skills', []))}
Location: {self.user_profile.get('location', '')}
Email: {self.user_profile.get('email', '')}
Phone: {self.user_profile.get('phone', '')}

RESUME SUMMARY:
{self.resume_data}

YOUR TASK:
Create a customized, ATS-optimized resume that:
1. Highlights the most relevant experience for THIS specific role
2. Uses keywords from the job description naturally
3. Reorders bullet points to put most relevant accomplishments first
4. Emphasizes skills and achievements that match job requirements
5. Maintains truthfulness - don't fabricate experience
6. Keeps professional formatting
7. Target length: 1-2 pages

FORMAT:
Use this clean text format (NOT markdown):

{self.user_profile.get('name', 'JIM ROME')}
{self.user_profile.get('location', '')} | {self.user_profile.get('email', '')} | {self.user_profile.get('phone', '')}

PROFESSIONAL SUMMARY
[2-3 sentences tailored to this role]

CORE COMPETENCIES
[List 8-12 relevant skills/competencies matching the job]

PROFESSIONAL EXPERIENCE

[Company Name] | [Location]
[Job Title] | [Dates]
- [Tailored bullet point emphasizing relevant achievement]
- [Tailored bullet point with quantified results]
- [Continue with most relevant bullets first]

[Repeat for other positions...]

EDUCATION
[Degree] | [School] | [Year]

TECHNICAL SKILLS
[Relevant technical skills for this role]

IMPORTANT: Output ONLY the resume text. No commentary, no markdown formatting, just the plain text resume."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            resume_content = response.content[0].text.strip()

            # Add footer with generation date
            resume_content += f"\n\n---\nCustomized for {job.get('company', '')} - {job.get('title', '')}\n"
            resume_content += f"Generated: {datetime.now().strftime('%Y-%m-%d')}\n"

            return resume_content

        except Exception as e:
            print(f"Error generating customized resume: {e}")
            return self._create_basic_resume(job)

    def _create_basic_resume(self, job: Dict) -> str:
        """Create a basic resume if AI generation fails."""
        return f"""JIM ROME
{self.user_profile.get('location', '')} | {self.user_profile.get('email', '')} | {self.user_profile.get('phone', '')}

PROFESSIONAL SUMMARY
{self.user_profile.get('current_role', 'Product Manager')} with {self.user_profile.get('years_experience', '')} years of experience.

SKILLS
{', '.join(self.user_profile.get('skills', []))}

RESUME DATA
{self.resume_data}

---
Customized for {job.get('company', '')} - {job.get('title', '')}
Generated: {datetime.now().strftime('%Y-%m-%d')}
"""

    def _sanitize_filename(self, text: str) -> str:
        """Sanitize text for use in filename."""
        # Remove special characters
        safe = ''.join(c for c in text if c.isalnum() or c in (' ', '-', '_'))
        # Replace spaces with underscores
        safe = safe.replace(' ', '_')
        # Limit length
        safe = safe[:50]
        return safe

    def batch_customize_resumes(self, jobs: List[Dict]) -> Dict[int, str]:
        """
        Customize resumes for multiple jobs.

        Returns dict mapping job index to resume filepath.
        """
        resume_files = {}

        print(f"\n🎯 Customizing resumes for {len(jobs)} jobs...")
        print(f"📁 Saving to: {self.output_dir}\n")

        for i, job in enumerate(jobs):
            try:
                filepath = self.customize_resume_for_job(job)
                resume_files[i] = filepath
                print(f"  ✓ Saved: {Path(filepath).name}")
            except Exception as e:
                print(f"  ✗ Error for {job.get('company', 'Unknown')}: {e}")

        print(f"\n✓ Generated {len(resume_files)} customized resumes")
        print(f"📂 Location: {self.output_dir}")

        return resume_files


def test_resume_customizer():
    """Test the resume customizer."""
    test_resume = """
    Product Manager with 8+ years of experience leading cross-functional teams.

    Experience:
    - Led product strategy for payments platform serving 10M users
    - Increased conversion by 25% through A/B testing
    - Managed $5M product budget
    """

    test_profile = {
        'name': 'Jim Rome',
        'email': 'romejim@gmail.com',
        'phone': '(555) 123-4567',
        'location': 'New York, NY',
        'current_role': 'Senior Product Manager',
        'years_experience': 8,
        'skills': ['Product Strategy', 'Data Analysis', 'A/B Testing', 'SQL', 'API Design']
    }

    test_job = {
        'company': 'Stripe',
        'title': 'Senior Product Manager, Payments',
        'description': 'We are looking for a PM to lead our payments infrastructure team...'
    }

    customizer = ResumeCustomizer(test_resume, test_profile)
    filepath = customizer.customize_resume_for_job(test_job)

    print(f"\n✓ Test resume created: {filepath}")

    with open(filepath, 'r') as f:
        print("\n" + "="*60)
        print(f.read())
        print("="*60)


if __name__ == '__main__':
    test_resume_customizer()
