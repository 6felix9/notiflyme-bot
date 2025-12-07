"""
Timezone configuration handler for NotiflyMeBot.

This module handles the /settimezone command to allow users to configure
their preferred timezone for accurate reminders.
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from utils.db import set_user_timezone, get_user_timezone
from zoneinfo import ZoneInfo, available_timezones, ZoneInfoNotFoundError
import logging

logger = logging.getLogger(__name__)

# Cache the set of valid timezones for performance
VALID_TIMEZONES = available_timezones()

COMMON_TIMEZONES = [
    "Asia/Singapore", 
    "America/New_York", 
    "America/Los_Angeles",
    "Europe/London", 
    "Europe/Paris", 
    "Asia/Tokyo", 
    "Australia/Sydney",
    "UTC"
]

# Validation constants
MAX_TIMEZONE_LENGTH = 50


async def settimezone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /settimezone command.
    
    Allows users to set their timezone or see their current setting.
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.message.from_user.id
    args = context.args
    
    # If no arguments, show current setting and help
    if not args:
        current_tz = get_user_timezone(user_id)
        
        tz_list_formatted = "\n".join([f"• `{tz}`" for tz in COMMON_TIMEZONES])
        
        message = (
            f"🌍 **Timezone Settings**\n\n"
            f"Your current timezone is: `{current_tz}`\n\n"
            f"To change it, use:\n`/settimezone <Region/City>`\n\n"
            f"Example:\n`/settimezone Europe/London`\n\n"
            f"**Common Timezones:**\n{tz_list_formatted}"
        )
        await update.message.reply_text(message, parse_mode="Markdown")
        return
    
    # Process timezone change request
    tz_input = args[0].strip()
    
    # Length validation
    if len(tz_input) > MAX_TIMEZONE_LENGTH:
        await update.message.reply_text("❌ Timezone name is too long. Please try again.")
        return
    
    # Explicit IANA validation (fast set lookup)
    if tz_input not in VALID_TIMEZONES:
        await update.message.reply_text(
            f"❌ Invalid timezone: `{tz_input}`.\n\n"
            "Please use a valid IANA timezone format (e.g., `Asia/Singapore`, `Europe/London`).",
            parse_mode="Markdown"
        )
        return
    
    # Additional safety: verify ZoneInfo can be constructed
    try:
        ZoneInfo(tz_input)
    except ZoneInfoNotFoundError:
        await update.message.reply_text(
            f"❌ Timezone `{tz_input}` is not available on this system.",
            parse_mode="Markdown"
        )
        return
    except Exception as e:
        logger.error(f"Unexpected error validating timezone {tz_input}: {e}")
        await update.message.reply_text("❌ An error occurred. Please try again.")
        return
    
    # Save to database
    if set_user_timezone(user_id, tz_input):
        await update.message.reply_text(f"✅ Timezone successfully set to: `{tz_input}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Failed to save timezone settings. Please try again.")


# Create the handler
timezone_handler = CommandHandler("settimezone", settimezone)

