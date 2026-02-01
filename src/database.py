"""Database configuration and utilities."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base


class Database:
    """Database manager."""

    def __init__(self, database_url: str = None):
        """Initialize database connection."""
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'sqlite:///data/jobs.db'
        )

        self.engine = create_engine(
            self.database_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={'check_same_thread': False} if 'sqlite' in self.database_url else {}
        )

        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        print("✓ Database tables created")

    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)
        print("✓ Database tables dropped")

    def get_session(self):
        """Get a database session."""
        return self.SessionLocal()

    def close(self):
        """Close database connection."""
        self.SessionLocal.remove()


# Global database instance
db = Database()
