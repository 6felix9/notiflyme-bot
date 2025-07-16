from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.db import get_database
from utils.gemini_dateparser import gemini_dateparser
from utils.time_converter import sgt_to_utc
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Get the MongoDB collection
db = get_database()
collection = db["reminders"]

# Define conversation states
WAITING_FOR_REMINDER = 1
WAITING_FOR_DATE = 2

# Set reminder command
async def setreminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "What would you like to be reminded of? Type /cancel to stop."
    )
    return WAITING_FOR_REMINDER

# Handle reminder input
async def handle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminder = update.message.text.strip()
    if not reminder:
        await update.message.reply_text("Reminder cannot be empty. Please try again.")
        return WAITING_FOR_REMINDER
    
    # Store the reminder
    context.user_data["reminder"] = reminder

    # Ask for the date
    await update.message.reply_text("When should I remind you? Type /cancel to stop.")
    return WAITING_FOR_DATE

# Handle date for reminder
async def handle_date(update, context: ContextTypes.DEFAULT_TYPE):
    user_date = update.message.text.strip()

    # Parse user input and get the SGT time
    sgt_time = gemini_dateparser(user_date)

    # Check for unhelpful input
    if sgt_time is None:
        await update.message.reply_text("I couldn't understand the date. Please try again.")
        return WAITING_FOR_DATE
    
    # Check if date is in the past
    now_sgt = datetime.now(ZoneInfo("Asia/Singapore"))
    if sgt_time <= now_sgt:
        await update.message.reply_text("❌ The date must be in the future. Please enter a future date.")
        return WAITING_FOR_DATE

    # Convert SGT time to UTC for storage
    utc_time = sgt_to_utc(sgt_time)

    # Store the time
    context.user_data["reminder_date"] = utc_time

    # Insert
    return await handle_insert(update, context, sgt_time)
    
# Insert reminder into the database
async def handle_insert(update: Update, context: ContextTypes.DEFAULT_TYPE, sgt_time):
    # Get the data items
    reminder = context.user_data["reminder"]
    reminder_date = context.user_data["reminder_date"]

    # Insert the reminder
    try:
        collection.insert_one({
            "user_id": update.message.from_user.id,
            "username": update.message.from_user.username,
            "reminder": reminder, 
            "reminder_date": reminder_date,
            "recurrence": "none",
            "sent": False,
            "created_at": datetime.now(timezone.utc),
        })
        # Confirm to user
        formatted_sgt_time = sgt_time.strftime("%A, %B %d at %I:%M %p")
        message = f"Got it! Reminder set for {formatted_sgt_time}"
        await update.message.reply_text(message)
        print("Success saving reminder!")
        return ConversationHandler.END
        
    except Exception as e:
        await update.message.reply_text(
            "❌ Sorry, something went wrong while saving your reminder. Please try again."
        )
        print(f"[ERROR] Failed to insert reminder: {e}")
    
    return ConversationHandler.END

# Cancel the reminder process
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
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