from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.db import get_database

# Get the MongoDB collection
db = get_database()
collection = db["reminders"]

# Conversation states
CONFIRM_DELETE = 1

# Clear all reminders
async def clearall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower() == "yes":
        result = collection.delete_many({})
        await update.message.reply_text(f"All reminders cleared. Deleted {result.deleted_count} reminders.")
    elif update.message.text.lower() == "no":
        await update.message.reply_text("Cancelled.")
    else:
        await update.message.reply_text("Invalid input. Please type 'yes' or 'no'.")
        return CONFIRM_DELETE
    return ConversationHandler.END

# Confirm clearing all reminders
async def confirm_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask the user to confirm clearing all reminders."""
    await update.message.reply_text(
        "Are you sure you want to clear all reminders? Type 'yes' to confirm or 'no' to cancel."
    )
    return CONFIRM_DELETE

# Conversation handler for clearing all reminders
clear_all_handler = ConversationHandler(
    entry_points=[CommandHandler("clearall", confirm_clear)],
    states={
        CONFIRM_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, clearall)],
    },
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)