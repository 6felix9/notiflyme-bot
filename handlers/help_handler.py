"""
Help command handler for NotiflyMeBot.

This module handles the /help command which provides
users with information about available commands.
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /help command.
    
    Sends a comprehensive help message listing all available
    commands and their descriptions.
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    message = (
        "Here are the commands you can use:\n\n"
        "• /start - Start the bot and see a welcome message.\n"
        "• /help - Display this help message.\n"
        "• /setreminder - Set a new reminder.\n"
        "• /listreminders - View all your upcoming reminders.\n"
        "• /cancel - Cancel any ongoing operation (like setting a reminder).\n"
        "• /clearall - Clear all reminders.\n\n"
        "💡 Tip: Reminders are set and shown in Singapore Time (SGT)."
    )
    await update.message.reply_text(message)


# Preconfigured CommandHandler for /help
help_handler = CommandHandler("help", help)