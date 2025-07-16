from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.helpers import escape_markdown
from utils.db import get_database
from zoneinfo import ZoneInfo
from datetime import datetime

db = get_database()
collection = db["reminders"]

async def listreminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    docs = list(collection.find({"user_id": user_id}))
    if not docs:
        await update.message.reply_text("❗️ You have no upcoming reminders.")
        return

    lines = []
    for doc in docs:
        reminder = doc.get("reminder", "<no text>")

        # 1. Pull naive datetime from MongoDB
        dt_utc_naive: datetime = doc["reminder_date"]

        # 2. Label it as UTC, then convert to SGT
        dt_utc = dt_utc_naive.replace(tzinfo=ZoneInfo("UTC"))
        dt_sgt = dt_utc.astimezone(ZoneInfo("Asia/Singapore"))

        # 3. Build date string as: Tuesday 16/5/2026, 6pm
        day_name = dt_sgt.strftime("%A")
        date_part = f"{dt_sgt.day}/{dt_sgt.month}/{dt_sgt.year}"
        time_part = dt_sgt.strftime("%-I%p").lower()  # e.g. '6pm'
        date_str = f"{day_name} {date_part}, {time_part}"

        # 4. Escape only the reminder text
        safe_reminder = escape_markdown(reminder, version=2)

        # 5. Combine into a bullet line with em-dash
        line = f"• *{safe_reminder}* — {date_str}"
        lines.append(line)

    header = "📋 *Your Upcoming Reminders*\n\n"
    footer = "\n\n_Use /cancel to stop reminders or /listreminders to refresh_"
    message = header + "\n".join(lines) + footer

    await update.message.reply_text(message, parse_mode="MarkdownV2")

list_reminders_handler = CommandHandler("listreminders", listreminders)
