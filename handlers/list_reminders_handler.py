"""
List reminders handler for NotiflyMeBot.

This module handles the /listreminders command which displays
all upcoming reminders for the user.
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.helpers import escape_markdown
from utils.db import get_reminders_collection
from utils.validation import validate_user_id
from utils.logger import setup_logger
from utils.exceptions import ValidationError
from zoneinfo import ZoneInfo
from datetime import datetime

# Set up logging
logger = setup_logger(__name__)

collection = get_reminders_collection()

from utils.auth import restricted


@restricted
async def listreminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /listreminders command.
    
    Retrieves and displays all upcoming reminders for the user
    in a formatted list with dates in Singapore timezone.
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    try:
        # Validate user ID
        user_id = validate_user_id(update.effective_user.id)
        
        docs = list(collection.find({"user_id": user_id}))
        
        if not docs:
            await update.message.reply_text("❗️ You have no upcoming reminders.")
            return

        lines = []
        for doc in docs:
            try:
                reminder = doc.get("reminder", "<no text>")

                # 1. Pull naive datetime from MongoDB
                dt_utc_naive: datetime = doc["reminder_date"]

                # 2. Label it as UTC, then convert to SGT
                dt_utc = dt_utc_naive.replace(tzinfo=ZoneInfo("UTC"))
                dt_sgt = dt_utc.astimezone(ZoneInfo("Asia/Singapore"))

                # 3. Build date string as: Tuesday 16/5/2026, 6pm
                day_name = dt_sgt.strftime("%A")
                date_part = f"{dt_sgt.day}/{dt_sgt.month}/{dt_sgt.year}"
                time_part = dt_sgt.strftime("%-I%p").lower()  # e.g. '6pm'
                date_str = f"{day_name} {date_part}, {time_part}"

                # 4. Escape only the reminder text
                safe_reminder = escape_markdown(reminder, version=2)

                # 5. Combine into a bullet line with em-dash
                line = f"• *{safe_reminder}* — {date_str}"
                lines.append(line)
                
            except Exception as e:
                logger.error(f"Error processing reminder document {doc.get('_id', 'unknown')}: {e}")
                # Skip this reminder and continue with others
                continue

        if not lines:
            await update.message.reply_text("❗️ No valid reminders found.")
            return

        header = "📋 *Your Upcoming Reminders*\n\n"
        footer = "\n\n_Use /cancel to stop reminders or /listreminders to refresh_"
        message = header + "\n".join(lines) + footer

        await update.message.reply_text(message, parse_mode="MarkdownV2")
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)}")
        logger.error(f"Validation error listing reminders: {e}")
        
    except Exception as e:
        await update.message.reply_text("❌ Sorry, something went wrong retrieving your reminders.")
        logger.error(f"Error listing reminders for user {update.effective_user.id}: {e}")

list_reminders_handler = CommandHandler("listreminders", listreminders)
