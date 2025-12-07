# NotiflyMeBot

A Telegram reminder bot that lets you set reminders using natural language. Simply tell it when you want to be reminded in plain English, and it will handle the rest.

## How It Works

1. **Set a Reminder**: Use `/setreminder` and type what you want to be reminded of
2. **Natural Language Date**: Enter when you want the reminder (e.g., "tomorrow at 3pm", "next Friday", "in 2 hours")
3. **AI Date Parsing**: Gemini AI converts your natural language into a precise datetime and stores it in MongoDB
4. **Automatic Delivery**: Background worker checks every 10 seconds and sends your reminder at the exact scheduled time

## Quick Start

### Docker (Recommended)

```bash
# Clone and navigate to the project
git clone <repository-url>
cd NotiflyMeBot

# Create environment file
cp .env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start MongoDB and Redis locally
# Then run the bot
python bot.py

# In separate terminals, start background workers
celery -A celery_worker worker --loglevel=info
celery -A celery_worker beat --loglevel=info
```

## Configuration

Required environment variables:

- `API_KEY` - Your Telegram Bot API token (from @BotFather)
- `GEMINI_API_KEY` - Google Gemini API key for natural language parsing
- `MONGO_URI` - MongoDB connection string (defaults to localhost)
- `REDIS_URL` - Redis connection URL (defaults to redis://redis:6379/0)

## Usage

- `/start` - Welcome message and basic information
- `/setreminder` - Create a new reminder (interactive conversation)
- `/listreminders` - View all your upcoming reminders
- `/settimezone` - Set your local timezone (default: Asia/Singapore)
- `/clearall` - Delete all your reminders
- `/help` - Show available commands
- `/cancel` - Cancel current operation

### Example

```
You: /setreminder
Bot: What would you like to be reminded of?
You: Call mom
Bot: When should I remind you?
You: tomorrow at 7pm
Bot: Got it! Reminder set for Tuesday, July 17 at 7:00 PM
```
