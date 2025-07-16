from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Help command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = (
        "Here are the commands you can use:\n\n"
        "• /start - Start the bot and see a welcome message.\n"
        "• /help - Display this help message.\n"
        "• /setreminder - Set a new reminder.\n"
        "• /listreminders - View all your upcoming reminders.\n"
        "• /cancel - Cancel any ongoing operation (like setting a reminder).\n"
        "• /clearall - Clear all reminders.\n\n"
        "💡 Tip: Use /setreminder to quickly add a reminder"
    )
    await update.message.reply_text(message)

# Preconfigured CommandHandler for /start
help_handler = CommandHandler("help", help)