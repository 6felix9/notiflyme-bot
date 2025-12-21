"""
Natural language date parsing using Groq API with Structured Outputs.

This module provides functionality to parse natural language date/time 
expressions into datetime objects using Groq's Structured Outputs (JSON Schema).
"""

import asyncio
import json
from typing import Optional
from config import GROQ_API_KEY
from groq import Groq
from pydantic import BaseModel, Field
from datetime import datetime, timezone
from utils.logger import setup_logger
from utils.exceptions import DateParsingError
from utils.validation import sanitize_for_llm
from zoneinfo import ZoneInfo

# Set up logging
logger = setup_logger(__name__)


class ParsedDate(BaseModel):
    """Schema for structured date parsing response."""
    sgt_datetime: Optional[str] = Field(
        None, description="ISO-8601 datetime string in Asia/Singapore timezone (e.g., 2025-12-21T15:00:00+08:00)"
    )
    valid: bool = Field(..., description="Whether the input was successfully parsed into a future date")


async def groq_dateparser(user_input: str) -> Optional[datetime]:
    """
    Parse natural language date/time expressions into datetime objects.
    Async wrapper to avoid blocking the event loop.
    
    Args:
        user_input: Natural language date/time expression
        
    Returns:
        datetime: Parsed datetime in SGT timezone, or None if parsing failed
    """
    try:
        # Validate input
        if not user_input or not user_input.strip():
            logger.warning("Empty user input provided to date parser")
            return None
            
        # Sanitize for LLM safety
        safe_input = sanitize_for_llm(user_input)
        if not safe_input:
            logger.warning("Input was completely sanitized (empty)")
            return None
            
        logger.debug(f"Parsing date input: '{safe_input}' (TZ: Asia/Singapore)")
        
        # Run the blocking Groq call in a thread pool
        return await asyncio.to_thread(_sync_groq_call, safe_input)
            
    except DateParsingError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in date parsing: {e}")
        raise DateParsingError(f"Unexpected error during date parsing: {e}")


def _sync_groq_call(user_input: str) -> Optional[datetime]:
    """
    Synchronous helper that makes the actual Groq API call with structured output.
    """
    user_timezone = "Asia/Singapore"
    try:
        # Define current time in user's timezone
        now_utc = datetime.now(timezone.utc)
        now_user = now_utc.astimezone(ZoneInfo(user_timezone))

        # Initialize Groq client
        try:
            client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Groq client: {e}")
            raise DateParsingError(f"Failed to initialize AI client: {e}")

        # Build the system prompt
        system_prompt = (
            f"You are a precise date and time parser. Current time: {now_user} ({user_timezone}). "
            "Convert the user's natural language date expression into an absolute ISO-8601 datetime string. "
            f"The result must be in the {user_timezone} timezone. "
            "If the input is ambiguous, assume the most likely upcoming future date. "
            "If the input cannot be parsed or refers to the past, set 'valid' to false. "
            "Output MUST follow the provided JSON schema."
        )

        # Make the Groq API call with structured output
        try:
            # Using kimi as in the user's example, as it supports structured outputs well
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "date_parsing_result",
                        "schema": ParsedDate.model_json_schema(),
                    },
                },
            )
            
            # Parse the response content
            content = response.choices[0].message.content
            parsed_data = ParsedDate.model_validate(json.loads(content))
            
        except Exception as e:
            logger.error(f"Groq API call or validation failed: {e}")
            raise DateParsingError(f"AI parsing service error: {e}")

        # Process the result
        if not parsed_data.valid or not parsed_data.sgt_datetime:
            logger.warning(f"Groq couldn't parse input: '{user_input}'")
            return None
        
        try:
            # Parse the datetime string
            dt_str = parsed_data.sgt_datetime
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            
            # Ensure it's timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo(user_timezone))
            else:
                # Ensure it matches the requested timezone
                dt = dt.astimezone(ZoneInfo(user_timezone))
            
            logger.debug(f"Successfully parsed '{user_input}' to {dt}")
            return dt
            
        except Exception as e:
            logger.error(f"Failed to process parsed datetime: {e}")
            return None

    except DateParsingError:
        raise
    except Exception as e:
        logger.error(f"Error in _sync_groq_call: {e}")
        return None
