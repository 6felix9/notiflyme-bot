"""
Celery worker configuration and task definitions.

This module configures the Celery application for background task processing
and defines scheduled tasks for checking and sending reminders.
"""

from celery import Celery
from reminder_tasks import send_due_reminders
from celery.schedules import crontab
from datetime import timedelta
from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery_app = Celery(
    "reminder_worker", 
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)


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