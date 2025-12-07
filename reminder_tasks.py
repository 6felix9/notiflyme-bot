"""
Background task processing for sending reminder notifications.

This module contains the task functions that run periodically to check
for due reminders and send them via Telegram.
"""

import asyncio
from datetime import datetime, timezone
from telegram import Bot
from telegram.error import TelegramError
from config import API_KEY
from utils.db import get_reminders_collection
from utils.logger import setup_logger
from utils.exceptions import DatabaseError

# Set up logging
logger = setup_logger(__name__)

# Get the MongoDB collection
collection = get_reminders_collection()

bot = Bot(token=API_KEY)


async def _send_telegram_message(user_id: int, text: str) -> bool:
    """
    Async helper to send a Telegram message.
    
    Args:
        user_id: Telegram user ID
        text: Message text
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        await bot.send_message(chat_id=user_id, text=f"🔔 Reminder: {text}")
        return True
    except TelegramError as e:
        logger.error(f"Telegram API error sending to {user_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to {user_id}: {e}")
        return False


def send_due_reminders() -> None:
    """
    Check for due reminders and send them via Telegram.
    
    Queries the database for reminders that are due (reminder_date <= now)
    and haven't been sent yet. Uses atomic find_one_and_update to prevent
    race conditions between multiple workers.
    
    This function is called periodically by the Celery scheduler.
    """
    try:
        now_utc = datetime.now(timezone.utc)
        
        # Process reminders one at a time with atomic updates to prevent race conditions
        while True:
            # Atomically find and claim a reminder
            # We look for documents that are due, not sent, and NOT currently processing
            reminder = collection.find_one_and_update(
                {
                    "reminder_date": {"$lte": now_utc},
                    "sent": False,
                    "processing": {"$ne": True}  # Avoid double processing
                },
                {
                    "$set": {"processing": True}  # Lock it
                },
                return_document=True
            )
            
            # If no more due reminders found, exit loop
            if reminder is None:
                break
            
            user_id = reminder["user_id"]
            text = reminder["reminder"]
            reminder_id = reminder["_id"]

            try:
                # Run the async send in a new event loop
                # This is necessary because Celery runs these tasks synchronously
                success = asyncio.run(_send_telegram_message(user_id, text))
                
                if success:
                    # Mark as sent and release lock
                    collection.update_one(
                        {"_id": reminder_id}, 
                        {"$set": {"sent": True, "processing": False}}
                    )
                    logger.info(f"Sent reminder: {text} to User ID: {user_id}")
                else:
                    # Internal failure (e.g. user blocked bot)
                    # We release the lock but DON'T mark as sent, so it might retry
                    # Or we could mark as 'failed' if we want to stop retrying.
                    # For now, just release lock.
                    collection.update_one(
                        {"_id": reminder_id}, 
                        {"$set": {"processing": False}}
                    )
                    
            except Exception as e:
                logger.error(f"Error processing individual reminder {reminder_id}: {e}")
                # Release lock on error
                collection.update_one(
                    {"_id": reminder_id}, 
                    {"$set": {"processing": False}}
                )
                
    except Exception as e:
        logger.error(f"Critical error in send_due_reminders: {e}")
        raise DatabaseError(f"Failed to check for due reminders: {e}")

