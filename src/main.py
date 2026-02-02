"""Main orchestrator for job search assistant."""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import db
from src.models import Job, UserProfile, Company, Contact
from src.resume_parser import ResumeParser
from src.job_aggregator import JobAggregator
from src.ai_matcher import JobMatcher
from src.email_service import EmailService
from src.sheets_service import SheetsService
from src.company_research import CompanyResearcher
from src.contact_finder import ContactFinder
from src.resume_customizer import ResumeCustomizer
from src.location_filter import matches_location_preference, get_location_score
from src.role_filter import is_product_manager_role, meets_seniority_requirement

from dotenv import load_dotenv
import yaml


class JobSearchAssistant:
    """Main job search assistant orchestrator."""

    def __init__(self):
        """Initialize the assistant."""
        # Load environment variables
        load_dotenv()

        # Load configuration
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Initialize database
        db.create_tables()
        self.session = db.get_session()

        # Initialize components
        self.resume_parser = ResumeParser(os.getenv('RESUME_DIRECTORY'))
        self.job_aggregator = JobAggregator(self.config)
        self.company_researcher = CompanyResearcher()
        self.contact_finder = ContactFinder()
        self.email_service = EmailService(os.getenv('USER_EMAIL'))

        # Initialize Google Sheets (optional)
        self.sheets_service = None
        if os.getenv('GOOGLE_SHEETS_ID'):
            try:
                self.sheets_service = SheetsService()
            except Exception as e:
                print(f"⚠ Could not initialize Google Sheets: {e}")

        # Parse resumes on first run
        self.resume_data = self.resume_parser.parse_all_resumes()
        self.resume_summary = self.resume_parser.get_resume_summary(self.resume_data)

        # Initialize user profile
        self.user_profile = self._get_or_create_user_profile()

        # Initialize AI matcher
        self.ai_matcher = JobMatcher(
            user_profile=self.config['user_profile'],
            resume_data=self.resume_summary
        )

        print("✓ Job Search Assistant initialized")

    def _get_or_create_user_profile(self) -> UserProfile:
        """Get or create user profile in database."""
        profile = self.session.query(UserProfile).first()

        if not profile:
            profile = UserProfile(
                name=self.config['user_profile']['name'],
                email=self.config['user_profile']['email'],
                phone=self.config['user_profile']['phone'],
                location=self.config['user_profile']['location'],
                current_role=self.config['user_profile']['current_role'],
                years_experience=self.config['user_profile']['years_experience'],
                skills=self.config['user_profile']['skills'],
                target_roles=list(self.config['matching_criteria']['required_keywords']),
                salary_min=int(os.getenv('MIN_SALARY', 150000)),
                salary_max=int(os.getenv('MAX_SALARY', 300000)),
                preferred_locations=os.getenv('PREFERRED_LOCATIONS', '').split(','),
                email_digest_times=os.getenv('DIGEST_TIMES', '08:00,18:00').split(','),
                min_match_score=float(os.getenv('MIN_MATCH_SCORE', 70)),
            )
            self.session.add(profile)
            self.session.commit()

        return profile

    def run_job_search(self):
        """Main job search workflow."""
        print("\n" + "="*60)
        print("🔍 Starting job search...")
        print("="*60 + "\n")

        # Step 1: Fetch new jobs
        print("Step 1: Fetching jobs from multiple sources...")
        jobs = self._fetch_jobs()

        if not jobs:
            print("No new jobs found.")
            return

        # Step 2: Score jobs with AI
        print(f"\nStep 2: Scoring {len(jobs)} jobs with AI matcher...")
        scored_jobs = self.ai_matcher.score_jobs_batch(jobs)

        # Step 3: Add location scores
        for job in scored_jobs:
            job['location_score'] = get_location_score(job.get('location', ''))

        # Step 4: Filter by minimum score
        min_score = self.user_profile.min_match_score
        filtered_jobs = [j for j in scored_jobs if j.get('match_score', 0) >= min_score]
        print(f"\n✓ {len(filtered_jobs)} jobs meet minimum score threshold ({min_score}%)")

        # Count Midtown jobs
        midtown_jobs = [j for j in filtered_jobs if j.get('location_score', 0) == 100]
        if midtown_jobs:
            print(f"  ⭐ {len(midtown_jobs)} Midtown Manhattan jobs (top priority!)")

        if not filtered_jobs:
            print("No jobs meet the minimum match score.")
            return

        # Sort by location preference first, then match score
        # This puts Midtown jobs at the top
        filtered_jobs.sort(key=lambda x: (x.get('location_score', 0), x.get('match_score', 0)), reverse=True)

        # Step 4: Save jobs to database
        print("\nStep 3: Saving jobs to database...")
        self._save_jobs_to_db(filtered_jobs)

        # Step 4.5: Sync to Google Sheets
        if self.sheets_service:
            print("\nSyncing jobs to Google Sheets...")
            self.sheets_service.add_jobs_to_sheet(filtered_jobs)

        # Step 5: Research companies for top jobs
        print("\nStep 4: Researching companies...")
        top_jobs = sorted(filtered_jobs, key=lambda x: x.get('match_score', 0), reverse=True)[:10]
        company_research = self.company_researcher.batch_research_companies(top_jobs)

        # Step 6: Identify potential contacts
        print("\nStep 5: Identifying potential contacts...")
        self._save_contacts_to_db(company_research)

        # Step 6.5: Find additional contacts with email guessing
        print("\nStep 5.5: Finding contact details and guessing emails...")
        self._find_and_save_detailed_contacts(top_jobs, company_research)

        # Step 6.7: Generate customized resumes for all matched jobs
        print("\nStep 5.7: Generating customized resumes for each job...")
        self._generate_customized_resumes(filtered_jobs)

        # Step 7: Send email digest
        print("\nStep 6: Sending email digest...")
        self._send_digest(filtered_jobs)

        print("\n" + "="*60)
        print("✓ Job search complete!")
        print("="*60)

    def _fetch_jobs(self) -> List[Dict]:
        """Fetch jobs from all sources."""
        keywords = self.config['matching_criteria']['required_keywords']
        locations = self.user_profile.preferred_locations

        jobs = self.job_aggregator.fetch_all_jobs(keywords, locations)

        # Filter out jobs already in database
        existing_external_ids = {
            job.external_id
            for job in self.session.query(Job).all()
        }

        new_jobs = [
            job for job in jobs
            if job.get('external_id') not in existing_external_ids
        ]

        # Filter by location (Manhattan/Bronx/Remote only)
        location_filtered_jobs = [
            job for job in new_jobs
            if matches_location_preference(job.get('location', ''))
        ]

        # Filter by role (Product Manager only, Senior+ level)
        role_filtered_jobs = [
            job for job in location_filtered_jobs
            if is_product_manager_role(job.get('title', '')) and
               meets_seniority_requirement(job.get('title', ''))
        ]

        print(f"✓ Found {len(new_jobs)} new jobs (filtered {len(jobs) - len(new_jobs)} duplicates)")
        print(f"✓ Location filtered: {len(location_filtered_jobs)} jobs match Manhattan/Bronx/Remote")
        print(f"✓ Role filtered: {len(role_filtered_jobs)} jobs are Product Manager roles (Senior+)")

        return role_filtered_jobs

    def _save_jobs_to_db(self, jobs: List[Dict]):
        """Save jobs to database."""
        for job_data in jobs:
            try:
                job = Job(
                    external_id=job_data.get('external_id'),
                    source=job_data.get('source'),
                    title=job_data.get('title'),
                    company=job_data.get('company'),
                    location=job_data.get('location'),
                    job_type=job_data.get('job_type'),
                    description=job_data.get('description'),
                    url=job_data.get('url'),
                    posted_date=job_data.get('posted_date'),
                    match_score=job_data.get('match_score', 0),
                    match_reasoning=job_data.get('match_reasoning', ''),
                    status='new',
                )
                self.session.add(job)

            except Exception as e:
                print(f"Error saving job: {e}")

        self.session.commit()
        print(f"✓ Saved {len(jobs)} jobs to database")

    def _save_contacts_to_db(self, company_research: Dict[str, Dict]):
        """Save potential contacts to database."""
        contact_count = 0

        for company_name, research in company_research.items():
            # Find jobs for this company
            jobs = self.session.query(Job).filter(
                Job.company == company_name
            ).all()

            for job in jobs:
                # Save contacts for this job
                for contact_data in research.get('potential_contacts', []):
                    contact = Contact(
                        job_id=job.id,
                        name=contact_data.get('name'),
                        title=contact_data.get('title'),
                        linkedin_url=contact_data.get('linkedin_url'),
                        relevance_score=contact_data.get('relevance_score'),
                        connection_reason=contact_data.get('connection_reason'),
                    )
                    self.session.add(contact)
                    contact_count += 1

        self.session.commit()
        print(f"✓ Saved {contact_count} potential contacts")

    def _find_and_save_detailed_contacts(self, jobs: List[Dict], company_research: Dict[str, Dict]):
        """Find detailed contacts with email guessing and LinkedIn URLs."""
        all_contacts = []

        for job in jobs:
            company_name = job.get('company', '')
            company_info = company_research.get(company_name, {})

            # Find contacts using the contact finder
            contacts = self.contact_finder.find_contacts_for_job(job, company_info)

            for contact in contacts:
                contact_entry = {
                    'job': f"{job.get('title', '')} at {company_name}",
                    'title': contact.get('title', ''),
                    'reasoning': contact.get('reasoning', ''),
                    'confidence': contact.get('confidence', ''),
                    'primary_email': contact.get('primary_email', ''),
                    'all_email_guesses': ', '.join(contact.get('email_guesses', [])[:3]),
                    'linkedin_search': contact.get('linkedin_search_url', ''),
                }
                all_contacts.append(contact_entry)

        # Sync to Google Sheets if available
        if self.sheets_service and all_contacts:
            self.sheets_service.add_contacts_to_sheet(all_contacts)

        print(f"✓ Found {len(all_contacts)} detailed contacts with email guesses")

    def _generate_customized_resumes(self, jobs: List[Dict]):
        """Generate customized resumes for each job."""
        if not jobs:
            return

        # Initialize resume customizer
        customizer = ResumeCustomizer(
            resume_data=self.resume_summary,
            user_profile=self.config['user_profile']
        )

        # Generate customized resumes
        resume_files = customizer.batch_customize_resumes(jobs)

        print(f"✓ Generated {len(resume_files)} customized resumes")
        print(f"📂 Saved in: customized_resumes/")

    def _send_digest(self, jobs: List[Dict]):
        """Send email digest."""
        # Determine if morning or evening
        current_hour = datetime.now().hour
        digest_type = 'morning' if current_hour < 14 else 'evening'

        # Get urgent jobs (posted recently or with deadline)
        urgent_jobs = [j for j in jobs if j.get('match_score', 0) >= 85][:3]

        self.email_service.send_digest(
            jobs=jobs,
            digest_type=digest_type,
            urgent_jobs=urgent_jobs,
        )

    def generate_application_materials(self, job_id: int):
        """Generate cover letter and application materials for a job."""
        job = self.session.query(Job).filter(Job.id == job_id).first()

        if not job:
            print(f"Job {job_id} not found")
            return

        print(f"\nGenerating application materials for: {job.title} at {job.company}")

        # Generate cover letter
        print("Generating cover letter...")
        cover_letter = self.ai_matcher.generate_cover_letter({
            'title': job.title,
            'company': job.company,
            'description': job.description,
        })

        print("\n" + "="*60)
        print("COVER LETTER")
        print("="*60)
        print(cover_letter)
        print("="*60)

        # Identify skill gaps
        print("\nIdentifying key preparation points...")
        gaps = self.ai_matcher.identify_key_gaps({
            'title': job.title,
            'company': job.company,
            'description': job.description,
        })

        print("\n" + "="*60)
        print("KEY PREPARATION POINTS")
        print("="*60)
        for i, gap in enumerate(gaps, 1):
            print(f"{i}. {gap}")
        print("="*60)

        # Get contacts for this job
        contacts = self.session.query(Contact).filter(Contact.job_id == job_id).all()

        if contacts:
            print("\n" + "="*60)
            print("RECOMMENDED CONTACTS")
            print("="*60)
            for contact in contacts[:3]:
                print(f"\n{contact.title}")
                print(f"Relevance: {contact.relevance_score}%")
                print(f"Why: {contact.connection_reason}")
                print(f"LinkedIn: {contact.linkedin_url}")

                # Generate outreach message
                outreach = self.company_researcher.generate_outreach_message(
                    contact={'name': contact.name, 'title': contact.title},
                    job_title=job.title,
                    company_name=job.company,
                    user_profile=self.config['user_profile']
                )
                print(f"\nSuggested message:\n{outreach}")
            print("="*60)

    def print_summary(self):
        """Print summary of current job search status."""
        total_jobs = self.session.query(Job).count()
        new_jobs = self.session.query(Job).filter(Job.status == 'new').count()
        high_matches = self.session.query(Job).filter(Job.match_score >= 80).count()

        print("\n" + "="*60)
        print("JOB SEARCH SUMMARY")
        print("="*60)
        print(f"Total jobs in database: {total_jobs}")
        print(f"New jobs to review: {new_jobs}")
        print(f"High match jobs (80%+): {high_matches}")
        print("="*60 + "\n")


def main():
    """Main entry point."""
    assistant = JobSearchAssistant()

    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == 'search':
            assistant.run_job_search()
        elif command == 'summary':
            assistant.print_summary()
        elif command == 'apply' and len(sys.argv) > 2:
            job_id = int(sys.argv[2])
            assistant.generate_application_materials(job_id)
        else:
            print("Unknown command. Available commands:")
            print("  python src/main.py search     - Run job search")
            print("  python src/main.py summary    - Show summary")
            print("  python src/main.py apply <id> - Generate application materials")
    else:
        # Default: run job search
        assistant.run_job_search()


if __name__ == '__main__':
    main()
