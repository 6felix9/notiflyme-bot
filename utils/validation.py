"""
Input validation and sanitization utilities for NotiflyMeBot.

This module provides functions to validate and sanitize user inputs
to prevent security issues and ensure data integrity.
"""

import re
from typing import Optional
from utils.logger import setup_logger
from utils.exceptions import ValidationError

# Set up logging
logger = setup_logger(__name__)

# Constants for validation
MAX_REMINDER_LENGTH = 1000
MAX_DATE_INPUT_LENGTH = 200
MIN_REMINDER_LENGTH = 1

# Patterns for validation
SAFE_TEXT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\.,!?\'"()-:;/@#$%&*+=_\[\]{}|\\`~\n\r]+$')
SUSPICIOUS_PATTERNS = [
    re.compile(r'<script', re.IGNORECASE),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'data:', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),
]


def sanitize_text(text: str) -> str:
    """
    Sanitize text input by removing potentially dangerous content.
    
    Args:
        text: Input text to sanitize
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Strip whitespace
    text = text.strip()
    
    # Remove null bytes and other control characters (except newlines/tabs/carriage returns)
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
    
    return text


def validate_reminder_text(text: str) -> str:
    """
    Validate and sanitize reminder text input.
    
    Args:
        text: Reminder text to validate
        
    Returns:
        str: Validated and sanitized text
        
    Raises:
        ValidationError: If validation fails
    """
    if not text or not isinstance(text, str):
        raise ValidationError("Reminder text is required")
    
    # Sanitize first
    text = sanitize_text(text)
    
    # Check length constraints
    if len(text) < MIN_REMINDER_LENGTH:
        raise ValidationError("Reminder text cannot be empty")
    
    if len(text) > MAX_REMINDER_LENGTH:
        raise ValidationError(f"Reminder text too long (max {MAX_REMINDER_LENGTH} characters)")
    
    # Check for suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Blocked suspicious pattern in reminder text: {text[:50]}...")
            raise ValidationError("Reminder text contains invalid content")
    
    # Log validation success
    logger.debug(f"Validated reminder text: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    return text


def validate_date_input(text: str) -> str:
    """
    Validate and sanitize date input text.
    
    Args:
        text: Date input text to validate
        
    Returns:
        str: Validated and sanitized text
        
    Raises:
        ValidationError: If validation fails
    """
    if not text or not isinstance(text, str):
        raise ValidationError("Date input is required")
    
    # Sanitize first
    text = sanitize_text(text)
    
    # Check length constraints
    if len(text) < 1:
        raise ValidationError("Date input cannot be empty")
    
    if len(text) > MAX_DATE_INPUT_LENGTH:
        raise ValidationError(f"Date input too long (max {MAX_DATE_INPUT_LENGTH} characters)")
    
    # Check for suspicious patterns
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.search(text):
            logger.warning(f"Blocked suspicious pattern in date input: {text[:50]}...")
            raise ValidationError("Date input contains invalid content")
    
    # Additional date-specific validation
    # Allow common date/time characters and words
    if not re.match(r'^[a-zA-Z0-9\s\.,!?\'"()-:;/@#\n\r]+$', text):
        logger.warning(f"Blocked invalid characters in date input: {text[:50]}...")
        raise ValidationError("Date input contains invalid characters")
    
    # Log validation success
    logger.debug(f"Validated date input: {text[:50]}{'...' if len(text) > 50 else ''}")
    
    return text


def validate_user_id(user_id: Optional[int]) -> int:
    """
    Validate Telegram user ID.
    
    Args:
        user_id: User ID to validate
        
    Returns:
        int: Validated user ID
        
    Raises:
        ValidationError: If validation fails
    """
    if user_id is None:
        raise ValidationError("User ID is required")
    
    if not isinstance(user_id, int):
        raise ValidationError("User ID must be an integer")
    
    if user_id <= 0:
        raise ValidationError("User ID must be positive")
    
    # Telegram user IDs are typically large positive integers
    if user_id > 2**63 - 1:  # Max signed 64-bit integer
        raise ValidationError("User ID is too large")
    
    return user_id


def validate_username(username: Optional[str]) -> Optional[str]:
    """
    Validate and sanitize Telegram username.
    
    Args:
        username: Username to validate (can be None)
        
    Returns:
        str or None: Validated username or None
        
    Raises:
        ValidationError: If validation fails
    """
    if username is None:
        return None
    
    if not isinstance(username, str):
        raise ValidationError("Username must be a string")
    
    # Sanitize
    username = sanitize_text(username)
    
    if not username:
        return None
    
    # Telegram username validation
    if not re.match(r'^[a-zA-Z0-9_]{1,32}$', username):
        logger.warning(f"Invalid Telegram username format: {username}")
        raise ValidationError("Invalid username format")
    
    return username