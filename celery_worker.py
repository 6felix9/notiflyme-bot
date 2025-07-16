from celery import Celery
from reminder_tasks import send_due_reminders
from celery.schedules import crontab
from datetime import timedelta

celery_app = Celery("reminder_worker", broker="redis://redis:6379/0")

@celery_app.task
def check_reminders():
    send_due_reminders()

celery_app.conf.beat_schedule = {
    "check-reminders-every-minute": {
        "task": "celery_worker.check_reminders",
        # "schedule": crontab(),  # every minute
        "schedule": timedelta(seconds=10)
    }
}