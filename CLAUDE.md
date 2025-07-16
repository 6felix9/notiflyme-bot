# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NotiflyMeBot is a Telegram reminder bot that allows users to set reminders using natural language. The bot stores reminders in MongoDB and uses Celery with Redis for background task processing to send reminders at the scheduled time.

## Development Commands

### Running the Bot
```bash
# Local development (requires MongoDB and Redis running)
python bot.py

# Docker development stack
docker-compose up

# Individual services
docker-compose up worker    # Celery worker
docker-compose up beat      # Celery beat scheduler
```

### Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (minimal - only used for package management)
npm install
```

### Database
- MongoDB runs on `mongodb://localhost:27017` (local) or `mongodb://mongodb:27017` (Docker)
- Database name: `telegram`
- Collection: `reminders`

### Background Tasks
```bash
# Run Celery worker manually
celery -A celery_worker worker --loglevel=info

# Run Celery beat scheduler manually  
celery -A celery_worker beat --loglevel=info
```

## Architecture

### Core Components

**bot.py** - Main application entry point that initializes the Telegram bot with handlers

**handlers/** - Telegram command handlers using conversation patterns:
- `set_reminder_handler.py` - Multi-step reminder creation with date parsing
- `list_reminders_handler.py` - Display user's reminders with SGT formatting
- `clear_all_handler.py` - Delete all user reminders
- `start_handler.py` / `help_handler.py` - Basic bot interaction

**utils/** - Core utilities:
- `db.py` - MongoDB connection management with environment-aware URI
- `gemini_dateparser.py` - Natural language date parsing using Gemini 2.0 Flash Lite
- `time_converter.py` - Timezone conversion between SGT and UTC

**reminder_tasks.py** - Background task that queries MongoDB for due reminders and sends them via Telegram

**celery_worker.py** - Celery configuration with Redis broker and beat scheduler (runs every 10 seconds)

### Data Flow

1. User sends `/setreminder` command
2. Bot prompts for reminder text and date using ConversationHandler
3. Gemini API parses natural language date input into SGT datetime
4. SGT time converted to UTC and stored in MongoDB with user metadata
5. Celery beat scheduler triggers reminder check every 10 seconds
6. Due reminders are sent via Telegram API and marked as sent

### Key Design Patterns

- **Conversation State Management**: Uses python-telegram-bot's ConversationHandler for multi-step interactions
- **Timezone Handling**: All times stored in UTC, displayed in SGT, with explicit timezone conversion
- **Error Handling**: Graceful degradation with user-friendly error messages for date parsing failures
- **Async/Await**: Consistent async pattern throughout Telegram handlers

### Environment Configuration

- `API_KEY` - Telegram Bot API token (stored in config.py)
- `GEMINI_API_KEY` - Google Gemini API key for date parsing (stored in config.py)
- `MONGO_URI` - MongoDB connection string (environment variable, defaults to localhost)
- Redis connection hardcoded to `redis://redis:6379/0` in Docker setup

### Database Schema

Reminders collection document structure:
```python
{
    "user_id": int,           # Telegram user ID
    "username": str,          # Telegram username
    "reminder": str,          # Reminder text
    "reminder_date": datetime, # UTC datetime when reminder should fire
    "recurrence": str,        # Always "none" (not implemented)
    "sent": bool,             # Whether reminder has been sent
    "created_at": datetime    # UTC timestamp of creation
}
```

### Security Considerations

- API keys are stored in config.py (should be moved to environment variables)
- MongoDB runs without authentication in Docker setup
- No rate limiting implemented for bot commands
- User input is escaped for Telegram MarkdownV2 formatting

## Testing

No test framework is currently implemented. Manual testing is done by:
1. Running the bot locally or in Docker
2. Interacting with the bot via Telegram
3. Verifying reminders are sent at the correct time
4. Checking MongoDB for correct data storage