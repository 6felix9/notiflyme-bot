"""
Configuration management for NotiflyMeBot.

This module handles loading and validating environment variables
required for the bot to function properly.
"""

import os
import sys
from typing import Optional


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


def get_env_var(key: str, required: bool = True, default: Optional[str] = None) -> str:
    """
    Get environment variable with validation.
    
    Args:
        key: Environment variable name
        required: Whether the variable is required
        default: Default value if not required and not set
        
    Returns:
        Environment variable value
        
    Raises:
        ConfigError: If required variable is missing
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ConfigError(f"Required environment variable '{key}' is not set")
    
    return value or ""


def validate_config() -> None:
    """
    Validate that all required configuration is present.
    
    Raises:
        ConfigError: If any required configuration is missing
    """
    required_vars = ["API_KEY", "GEMINI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}\n\n"
            "Please set the following environment variables:\n"
            "- API_KEY: Your Telegram Bot API token\n"
            "- GEMINI_API_KEY: Your Google Gemini API key\n"
            "- MONGO_URI: MongoDB connection string (optional, defaults to localhost)\n"
            "- REDIS_URL: Redis connection URL (optional, defaults to redis://redis:6379/0)"
        )
        raise ConfigError(error_msg)


# Load and validate configuration
try:
    validate_config()
except ConfigError as e:
    print(f"Configuration Error: {e}", file=sys.stderr)
    sys.exit(1)

# Export configuration variables
API_KEY = get_env_var("API_KEY")
GEMINI_API_KEY = get_env_var("GEMINI_API_KEY")
MONGO_URI = get_env_var("MONGO_URI", required=False, default="mongodb://localhost:27017")
REDIS_URL = get_env_var("REDIS_URL", required=False, default="redis://redis:6379/0")

# Database configuration
DATABASE_NAME = "telegram"
REMINDERS_COLLECTION = "reminders"

# Celery configuration
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Timezone settings
DEFAULT_TIMEZONE = "Asia/Singapore"