"""
Custom exception classes for NotiflyMeBot.

This module defines application-specific exceptions to provide
more granular error handling and better error messages.
"""


class NotiflyMeBotError(Exception):
    """Base exception class for NotiflyMeBot application."""
    pass


class DatabaseError(NotiflyMeBotError):
    """Raised when database operations fail."""
    pass


class DateParsingError(NotiflyMeBotError):
    """Raised when date parsing fails."""
    pass


class ValidationError(NotiflyMeBotError):
    """Raised when input validation fails."""
    pass


class TelegramAPIError(NotiflyMeBotError):
    """Raised when Telegram API operations fail."""
    pass


class ConfigurationError(NotiflyMeBotError):
    """Raised when configuration is invalid or missing."""
    pass