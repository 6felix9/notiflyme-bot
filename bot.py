from config import API_KEY
from telegram.ext import ApplicationBuilder
from handlers.start_handler import start_handler
from handlers.help_handler import help_handler
from handlers.set_reminder_handler import set_reminder_handler
from handlers.list_reminders_handler import list_reminders_handler
from handlers.clear_all_handler import clear_all_handler

def main():
    # Initialize the Telegram bot application
    application = ApplicationBuilder().token(API_KEY).build()

    # Add handlers
    application.add_handler(start_handler)
    application.add_handler(help_handler)
    application.add_handler(set_reminder_handler)
    application.add_handler(list_reminders_handler)
    application.add_handler(clear_all_handler)

    # Run the bot
    application.run_polling()
    
if __name__ == "__main__":
    main()