"""Scheduler to run job search 2x daily."""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from src.main import JobSearchAssistant
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('job_search.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def run_job_search():
    """Run the job search workflow."""
    try:
        logger.info("="*60)
        logger.info("Starting scheduled job search")
        logger.info("="*60)

        assistant = JobSearchAssistant()
        assistant.run_job_search()

        logger.info("Scheduled job search completed successfully")

    except Exception as e:
        logger.error(f"Error running scheduled job search: {e}", exc_info=True)


def main():
    """Set up and start the scheduler."""
    scheduler = BlockingScheduler()

    # Schedule morning run at 8:00 AM
    scheduler.add_job(
        run_job_search,
        CronTrigger(hour=8, minute=0),
        id='morning_job_search',
        name='Morning Job Search',
        replace_existing=True
    )

    # Schedule evening run at 6:00 PM
    scheduler.add_job(
        run_job_search,
        CronTrigger(hour=18, minute=0),
        id='evening_job_search',
        name='Evening Job Search',
        replace_existing=True
    )

    logger.info("Scheduler started. Job search will run at:")
    logger.info("  - 8:00 AM (Morning digest)")
    logger.info("  - 6:00 PM (Evening digest)")
    logger.info("\nPress Ctrl+C to exit")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")


if __name__ == '__main__':
    main()
