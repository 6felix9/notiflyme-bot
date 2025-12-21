"""
Start command handler for NotiflyMeBot.

This module handles the /start command which provides
a welcome message to new users.
"""

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler


from utils.auth import restricted


@restricted
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle the /start command.
    
    Sends a welcome message to the user with basic instructions
    on how to use the bot.
    
    Args:
        update: Telegram update object
        context: Telegram context object
    """
    await update.message.reply_text(
        "Hello! Use /setreminder to set a reminder or /help see more what I can do!"
    )


# Preconfigured CommandHandler for /start
start_handler = CommandHandler("start", start)