"""Database models for job search assistant."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Job(Base):
    """Job listing model."""

    __tablename__ = 'jobs'

    id = Column(Integer, primary_key=True)
    external_id = Column(String(255), unique=True, nullable=False)
    source = Column(String(50), nullable=False)  # linkedin, indeed, etc.

    # Basic info
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255))
    job_type = Column(String(50))  # Full-time, Contract, etc.
    work_arrangement = Column(String(50))  # Remote, Hybrid, On-site

    # Details
    description = Column(Text)
    requirements = Column(Text)
    salary_min = Column(Integer)
    salary_max = Column(Integer)

    # URLs
    url = Column(String(500))
    company_url = Column(String(500))

    # Matching
    match_score = Column(Float, default=0.0)
    match_reasoning = Column(Text)

    # Metadata
    posted_date = Column(DateTime)
    deadline = Column(DateTime)
    discovered_date = Column(DateTime, default=datetime.utcnow)

    # Status
    status = Column(String(50), default='new')  # new, reviewed, applied, rejected, expired

    # Relationships
    company_info = relationship('Company', back_populates='jobs', uselist=False)
    applications = relationship('Application', back_populates='job')
    contacts = relationship('Contact', back_populates='job')

    def __repr__(self):
        return f"<Job(title='{self.title}', company='{self.company}', score={self.match_score})>"


class Company(Base):
    """Company information model."""

    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))

    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    size = Column(String(50))
    funding_stage = Column(String(50))
    total_funding = Column(String(50))

    description = Column(Text)
    website = Column(String(500))
    linkedin_url = Column(String(500))

    # Culture data
    glassdoor_rating = Column(Float)
    culture_keywords = Column(JSON)

    tech_stack = Column(JSON)

    last_updated = Column(DateTime, default=datetime.utcnow)

    # Relationships
    jobs = relationship('Job', back_populates='company_info')

    def __repr__(self):
        return f"<Company(name='{self.name}', industry='{self.industry}')>"


class Contact(Base):
    """Potential contacts at companies."""

    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))

    name = Column(String(255))
    title = Column(String(255))
    linkedin_url = Column(String(500))

    # Why they're a good contact
    relevance_score = Column(Float)
    connection_reason = Column(Text)

    # Outreach tracking
    contacted = Column(Boolean, default=False)
    contacted_date = Column(DateTime)
    response_received = Column(Boolean, default=False)
    notes = Column(Text)

    # Relationships
    job = relationship('Job', back_populates='contacts')

    def __repr__(self):
        return f"<Contact(name='{self.name}', title='{self.title}')>"


class Application(Base):
    """Job application tracking."""

    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('jobs.id'))

    # Application details
    applied_date = Column(DateTime, default=datetime.utcnow)
    resume_version = Column(String(255))  # Which resume was used
    cover_letter = Column(Text)

    # Status tracking
    status = Column(String(50), default='submitted')
    # submitted, phone_screen, interview, offer, rejected

    status_history = Column(JSON)  # Track status changes

    # Follow-ups
    last_contact_date = Column(DateTime)
    next_follow_up = Column(DateTime)

    notes = Column(Text)

    # Relationships
    job = relationship('Job', back_populates='applications')

    def __repr__(self):
        return f"<Application(job_id={self.job_id}, status='{self.status}')>"


class UserProfile(Base):
    """User profile and preferences."""

    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)

    # Basic info
    name = Column(String(255))
    email = Column(String(255))
    phone = Column(String(50))
    location = Column(String(255))

    # Career info
    current_role = Column(String(255))
    years_experience = Column(Integer)

    # Parsed resume data
    skills = Column(JSON)
    experience = Column(JSON)
    education = Column(JSON)

    # Preferences
    target_roles = Column(JSON)
    target_companies = Column(JSON)
    excluded_companies = Column(JSON)

    salary_min = Column(Integer)
    salary_max = Column(Integer)

    preferred_locations = Column(JSON)
    work_arrangements = Column(JSON)

    # Settings
    email_digest_times = Column(JSON)
    min_match_score = Column(Float, default=70.0)

    last_updated = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<UserProfile(name='{self.name}', email='{self.email}')>"


class EmailDigest(Base):
    """Email digest history."""

    __tablename__ = 'email_digests'

    id = Column(Integer, primary_key=True)
    sent_date = Column(DateTime, default=datetime.utcnow)

    jobs_included = Column(JSON)  # List of job IDs
    recipient = Column(String(255))

    digest_type = Column(String(50))  # morning, evening

    opened = Column(Boolean, default=False)
    jobs_clicked = Column(JSON)

    def __repr__(self):
        return f"<EmailDigest(sent_date='{self.sent_date}', type='{self.digest_type}')>"
