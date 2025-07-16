"""
Clear all reminders handler for NotiflyMeBot.

This module handles the /clearall command which allows users
to delete all their reminders with confirmation.
"""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from utils.db import get_reminders_collection

# Get the MongoDB collection
collection = get_reminders_collection()

# Conversation states
CONFIRM_DELETE = 1


async def clearall(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle user confirmation for clearing all reminders.
    
    Processes the user's yes/no response and either deletes all
    their reminders or cancels the operation.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: ConversationHandler.END to end the conversation
    """
    if update.message.text.lower() == "yes":
        user_id = update.effective_user.id
        result = collection.delete_many({"user_id": user_id})
        await update.message.reply_text(f"All your reminders cleared. Deleted {result.deleted_count} reminders.")
    elif update.message.text.lower() == "no":
        await update.message.reply_text("Cancelled.")
    else:
        await update.message.reply_text("Invalid input. Please type 'yes' or 'no'.")
        return CONFIRM_DELETE
    return ConversationHandler.END


async def confirm_clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Ask the user to confirm clearing all reminders.
    
    Prompts the user with a confirmation message before
    proceeding with deleting all reminders.
    
    Args:
        update: Telegram update object
        context: Telegram context object
        
    Returns:
        int: CONFIRM_DELETE state to wait for user confirmation
    """
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