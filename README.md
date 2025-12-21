# NotiflyMeBot

A Telegram reminder bot that lets you set reminders using natural language. Simply tell it when you want to be reminded in plain English, and it will handle the rest.

## How It Works

1. **Set a Reminder**: Use `/setreminder` and type what you want to be reminded of
2. **Natural Language Date**: Enter when you want the reminder (e.g., "tomorrow at 3pm", "next Friday", "in 2 hours")
3. **AI Date Parsing**: Groq AI converts your natural language into a precise datetime and stores it in MongoDB
4. **Automatic Delivery**: Background worker checks every 10 seconds and sends your reminder at the exact scheduled time

## Deployment Guide

Follow these steps to deploy the bot to your remote instance using Docker.

### 1. Build and Push (From your local machine)

Build the Docker image for **arm64** (common for modern cloud instances) and push it to Docker Hub.

```bash
# Build the image for arm64
docker build --platform linux/arm64 -t felixlmao/notiflyme-bot:latest .

# Log in and push
docker login
docker push felixlmao/notiflyme-bot:latest
```

### 2. Setup Instance (On your remote server)

On your remote instance, create a directory and the `.env` file.

```bash
mkdir ~/notiflyme-bot && cd ~/notiflyme-bot
nano .env
```

Add your production credentials:
```text
API_KEY=your_telegram_bot_token
GROQ_API_KEY=your_groq_api_key
AUTHORIZED_USER_ID=1522275008
```

### 3. Deploy and Run

Create or copy `docker-compose.yml` to the instance, then run:

```bash
# Pull and start services in background
docker pull felixlmao/notiflyme-bot:latest
docker compose up -d
```

To view logs: `docker compose logs -f`

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
- `GROQ_API_KEY` - Groq API key for natural language date parsing
- `AUTHORIZED_USER_ID` - Your Telegram User ID (only this user can use the bot)
- `MONGO_URI` - MongoDB connection string (e.g., `mongodb://mongodb:27017` in Docker)
- `REDIS_URL` - Redis connection URL (e.g., `redis://redis:6379/0` in Docker)

## Usage

- `/start` - Welcome message and basic information
- `/setreminder` - Create a new reminder (interactive conversation)
- `/listreminders` - View all your upcoming reminders
- `/clearall` - Delete all your reminders
- `/help` - Show available commands
- `/cancel` - Cancel current operation

> [!NOTE]
> All reminders use **Singapore Time (SGT)**. The bot is hardcoded to SGT for consistency.

### Example

```
You: /setreminder
Bot: What would you like to be reminded of?
You: Call mom
Bot: When should I remind you?
You: tomorrow at 7pm
Bot: Got it! Reminder set for Tuesday, July 17 at 7:00 PM
```
