"""
Background task processing for sending reminder notifications.

This module contains the task functions that run periodically to check
for due reminders and send them via Telegram.
"""

from datetime import datetime, timezone
from telegram import Bot
from telegram.error import TelegramError
from config import API_KEY
from utils.db import get_reminders_collection
from utils.logger import setup_logger
from utils.exceptions import DatabaseError, TelegramAPIError

# Set up logging
logger = setup_logger(__name__)

# Get the MongoDB collection
collection = get_reminders_collection()

bot = Bot(token=API_KEY)


def send_due_reminders() -> None:
    """
    Check for due reminders and send them via Telegram.
    
    Queries the database for reminders that are due (reminder_date <= now)
    and haven't been sent yet, then sends them via Telegram and marks them as sent.
    
    This function is called periodically by the Celery scheduler.
    
    Raises:
        DatabaseError: If database operations fail
    """
    try:
        now_utc = datetime.now(timezone.utc)
        due = collection.find({
            "reminder_date": {"$lte": now_utc},
            "sent": False
        })

        for reminder in due:
            user_id = reminder["user_id"]
            text = reminder["reminder"]
            reminder_id = reminder["_id"]

            try:
                # Send the reminder via Telegram
                bot.send_message(chat_id=user_id, text=f"🔔 Reminder: {text}")
                
                # Mark as sent in database
                collection.update_one(
                    {"_id": reminder_id}, 
                    {"$set": {"sent": True}}
                )
                
                logger.info(f"Sent reminder: {text} to User ID: {user_id}")
                
            except TelegramError as e:
                logger.error(f"Telegram API error sending reminder to User ID {user_id}: {e}")
                # Don't mark as sent if Telegram API failed
                
            except Exception as e:
                logger.error(f"Database error updating reminder {reminder_id}: {e}")
                # Reminder was sent but couldn't mark as sent - log warning
                logger.warning(f"Reminder sent to {user_id} but database update failed")
                
    except Exception as e:
        logger.error(f"Critical error in send_due_reminders: {e}")
        raise DatabaseError(f"Failed to check for due reminders: {e}")

