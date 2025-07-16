from datetime import datetime, timezone
from telegram import Bot
from config import API_KEY
from utils.db import get_database

# Get the MongoDB collection
db = get_database()
collection = db["reminders"]

bot = Bot(token=API_KEY)

def send_due_reminders():
    now_utc = datetime.now(timezone.utc)
    due = collection.find({
        "reminder_date": {"$lte": now_utc},
        "sent": False
    })

    for reminder in due:
        user_id = reminder["user_id"]
        text = reminder["reminder"]

        try:
            bot.send_message(chat_id=user_id, text=f"🔔 Reminder: {text}")
            collection.update_one({"_id": reminder["_id"]}, {"$set": {"sent": True}})
            print(f"Sent reminder: {text} to User ID: {user_id}")
        except Exception as e:
            print(f"[ERROR] Failed to send reminder: {e}")

