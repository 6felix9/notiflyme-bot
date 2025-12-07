"""
Celery worker configuration and task definitions.

This module configures the Celery application for background task processing
and defines scheduled tasks for checking and sending reminders.
"""

from celery import Celery
from celery.signals import worker_ready
from reminder_tasks import send_due_reminders
from celery.schedules import crontab
from datetime import timedelta
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from utils.db import get_reminders_collection
from utils.logger import setup_logger

logger = setup_logger(__name__)

celery_app = Celery(
    "reminder_worker", 
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)


@worker_ready.connect
def cleanup_stale_processing_locks(sender=None, **kwargs):
    """
    Reset any reminders stuck in processing state from crashed workers.
    
    This runs when a Celery worker starts up to ensure no reminders
    are permanently locked due to a previous worker crash.
    """
    try:
        collection = get_reminders_collection()
        result = collection.update_many(
            {"processing": True},
            {"$set": {"processing": False}}
        )
        if result.modified_count > 0:
            logger.warning(f"Cleaned up {result.modified_count} stale processing locks on worker startup")
    except Exception as e:
        logger.error(f"Failed to cleanup stale processing locks: {e}")


@celery_app.task
def check_reminders() -> None:
    """
    Celery task to check for and send due reminders.
    
    This task is scheduled to run every 10 seconds by the Celery beat scheduler.
    It delegates the actual work to the send_due_reminders function.
    """
    send_due_reminders()


celery_app.conf.beat_schedule = {
    "check-reminders-every-minute": {
        "task": "celery_worker.check_reminders",
        # "schedule": crontab(),  # every minute
        "schedule": timedelta(seconds=10)
    }
}