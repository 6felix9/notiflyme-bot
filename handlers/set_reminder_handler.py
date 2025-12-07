"""
Set reminder handler for NotiflyMeBot.

This module handles the /setreminder command which allows users
to create new reminders through a multi-step conversation.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.db import get_reminders_collection, get_user_timezone
from utils.gemini_dateparser import gemini_dateparser
from utils.time_converter import sgt_to_utc
from utils.logger import setup_logger
from utils.validation import validate_reminder_text, validate_date_input, validate_user_id, validate_username
from utils.exceptions import ValidationError
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Set up logging
logger = setup_logger(__name__)

# Get the MongoDB collection
collection = get_reminders_collection()

# Define conversation states
WAITING_FOR_REMINDER = 1
WAITING_FOR_DATE = 2

# Set reminder command
async def setreminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Start the reminder creation process.
    
    Initiates a conversation to collect reminder details from the user.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: WAITING_FOR_REMINDER state to wait for reminder text
    """
    await update.message.reply_text(
        "What would you like to be reminded of? Type /cancel to stop."
    )
    return WAITING_FOR_REMINDER

# Handle reminder input
async def handle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user input for reminder text.
    
    Validates and stores the reminder text, then prompts for the date.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: WAITING_FOR_DATE state or WAITING_FOR_REMINDER if validation fails
    """
    try:
        # Validate and sanitize reminder text
        reminder = validate_reminder_text(update.message.text)
        
        # Store the reminder
        context.user_data["reminder"] = reminder

        # Ask for the date
        await update.message.reply_text("When should I remind you? Type /cancel to stop.")
        return WAITING_FOR_DATE
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)} Please try again.")
        return WAITING_FOR_REMINDER
    except Exception as e:
        logger.error(f"Unexpected error validating reminder: {e}")
        await update.message.reply_text("❌ Something went wrong. Please try again.")
        return WAITING_FOR_REMINDER

# Handle date for reminder
async def handle_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user input for reminder date/time.
    
    Validates the date input, parses it using AI, converts to appropriate
    timezone, and proceeds to save the reminder.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: ConversationHandler.END or WAITING_FOR_DATE if validation fails
    """
    try:
        # Validate and sanitize date input
        user_date = validate_date_input(update.message.text)
        
        # Get user's timezone preference
        user_tz = get_user_timezone(update.message.from_user.id)

        # Parse user input and get the time in user's timezone (using AI async call)
        await update.message.reply_chat_action("typing")  # Show typing indicator
        parsed_time = await gemini_dateparser(user_date, user_tz)

        # Check for unhelpful input
        if parsed_time is None:
            await update.message.reply_text("I couldn't understand the date. Please try again.")
            return WAITING_FOR_DATE
        
        # Defensive check: ensure parsed_time has timezone info
        if parsed_time.tzinfo is None:
            logger.warning(f"Parsed time missing tzinfo, defaulting to user timezone: {user_tz}")
            parsed_time = parsed_time.replace(tzinfo=ZoneInfo(user_tz))
        
        # Check if date is in the past
        # We compare against current time in the user's timezone
        now_local = datetime.now(parsed_time.tzinfo)
        if parsed_time <= now_local:
            await update.message.reply_text("❌ The date must be in the future. Please enter a future date.")
            return WAITING_FOR_DATE

        # Convert local time to UTC for storage
        utc_time = sgt_to_utc(parsed_time)  # sgt_to_utc handles generic awareness

        # Store the time
        context.user_data["reminder_date"] = utc_time

        # Insert
        return await handle_insert(update, context, parsed_time)
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)} Please try again.")
        return WAITING_FOR_DATE
    except Exception as e:
        logger.error(f"Unexpected error processing date: {e}")
        await update.message.reply_text("❌ Something went wrong processing the date. Please try again.")
        return WAITING_FOR_DATE
    
# Insert reminder into the database
async def handle_insert(update: Update, context: ContextTypes.DEFAULT_TYPE, parsed_time) -> int:
    """
    Insert the validated reminder into the database.
    
    Validates user information and saves the reminder with all
    necessary metadata to the database.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        parsed_time: Parsed reminder time in User's timezone
        
    Returns:
        int: ConversationHandler.END
    """
    try:
        # Get and validate the data items
        reminder = context.user_data["reminder"]
        reminder_date = context.user_data["reminder_date"]
        
        # Validate user data
        user_id = validate_user_id(update.message.from_user.id)
        username = validate_username(update.message.from_user.username)

        # Insert the reminder
        collection.insert_one({
            "user_id": user_id,
            "username": username,
            "reminder": reminder, 
            "reminder_date": reminder_date,
            "recurrence": "none",
            "sent": False,
            "created_at": datetime.now(timezone.utc),
        })
        
        # Confirm to user
        # Confirm to user
        formatted_time = parsed_time.strftime("%A, %B %d at %I:%M %p")
        message = f"Got it! Reminder set for {formatted_time}"
        await update.message.reply_text(message)
        logger.info(f"Successfully saved reminder for user {user_id}: {reminder}")
        return ConversationHandler.END
        
    except ValidationError as e:
        await update.message.reply_text(f"❌ {str(e)} Please try again.")
        logger.error(f"Validation error saving reminder: {e}")
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Sorry, something went wrong while saving your reminder. Please try again."
        )
        logger.error(f"Failed to insert reminder: {e}")
    
    return ConversationHandler.END

# Cancel the reminder process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel the reminder creation process.
    
    Ends the conversation and informs the user that the
    reminder creation has been cancelled.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: ConversationHandler.END
    """
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

# Conversation handler for setting reminders
set_reminder_handler = ConversationHandler(
    entry_points=[CommandHandler("setreminder", setreminder)],
    states={
        WAITING_FOR_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reminder)],
        WAITING_FOR_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_date)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)