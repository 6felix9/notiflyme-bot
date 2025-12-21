"""
Authentication utilities for NotiflyMeBot.
"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from config import AUTHORIZED_USER_ID, DEFAULT_TIMEZONE
from utils.logger import setup_logger

logger = setup_logger(__name__)

def restricted(func):
    """Decorator to restrict access to the authorized user only."""
    @wraps(func)
    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id != AUTHORIZED_USER_ID:
            logger.warning(f"Unauthorized access attempt by user {user_id}")
            await update.message.reply_text("You are not authorised to use this bot.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapped
