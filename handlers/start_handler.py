from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Use /setreminder to set a reminder or /help see more what I can do!")

# Preconfigured CommandHandler for /start
start_handler = CommandHandler("start", start)