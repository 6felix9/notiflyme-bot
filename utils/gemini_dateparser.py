"""
Natural language date parsing using Google Gemini API.

This module provides functionality to parse natural language date/time 
expressions into datetime objects using Google's Gemini 2.0 Flash Lite model.
"""

from typing import Optional
from config import GEMINI_API_KEY
from google import genai
from google.genai import types
from pydantic import BaseModel
from datetime import datetime, timezone
from utils.time_converter import utc_to_sgt
from utils.logger import setup_logger
from utils.exceptions import DateParsingError
from zoneinfo import ZoneInfo

# Set up logging
logger = setup_logger(__name__)


def gemini_dateparser(user_input: str) -> Optional[datetime]:
    """
    Parse natural language date/time expressions into datetime objects.
    
    Uses Google Gemini 2.0 Flash Lite to convert natural language inputs like
    "tomorrow at 3pm", "next Friday", "in 2 hours" into proper datetime objects
    in Singapore timezone.
    
    Args:
        user_input: Natural language date/time expression
        
    Returns:
        datetime: Parsed datetime in Singapore timezone, or None if parsing failed
        
    Raises:
        DateParsingError: If parsing fails due to API or validation errors
    """
    try:
        # Validate input
        if not user_input or not user_input.strip():
            logger.warning("Empty user input provided to date parser")
            return None
            
        user_input = user_input.strip()
        logger.debug(f"Parsing date input: '{user_input}'")
        
        # Define variables
        now_utc = datetime.now(timezone.utc)
        now_sgt = utc_to_sgt(now_utc)

        # Step 1: Define schema
        class ParsedDate(BaseModel):
            sgt_datetime: datetime  # ISO 8601 string in SGT
            original_input: str

        # Step 2: Initialize Gemini client
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise DateParsingError(f"Failed to initialize AI client: {e}")

        # Step 3: Gemini content generation call
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=f"{user_input}",
                config=types.GenerateContentConfig(
                system_instruction=(
                        "You are a helpful date and time parser. "
                        "You will convert natural language expressions such as 'in two hours', 'next Friday 3pm', or 'tomorrow evening' into an absolute date and time. "
                        "I will give you the current time in Singapore Time (SGT), and you must calculate the result based on that SGT time. "
                        "You must return the resulting datetime in **SGT**, not UTC. "
                        f"The current time in SGT is {now_sgt}"
                        "Respond in the following JSON format:\n"
                        "{ \"sgt_datetime\": \"...\", \"original_input\": \"...\" }"
                        "If you cannot understand the input or it does not make sense as a future date, "
                        "set both values to 0:\n"
                        "{ \"sgt_datetime\": 0, \"original_input\": 0 }"
                    ),
                    response_mime_type="application/json",
                    response_schema=ParsedDate
                )
            )
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise DateParsingError(f"AI parsing service unavailable: {e}")

        # Step 4: Process the response
        try:
            parsed_result: ParsedDate = response.parsed
            
            # Check for error in Gemini response
            if parsed_result is None:
                logger.warning(f"Gemini returned None for input: '{user_input}'")
                return None
            
            dt = parsed_result.sgt_datetime
            
            # Check if Gemini indicated it couldn't parse the input
            if dt == 0 or isinstance(dt, int):
                logger.warning(f"Gemini couldn't parse input: '{user_input}'")
                return None
            
            # Ensure it's timezone-aware
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo("Asia/Singapore"))
            
            logger.debug(f"Successfully parsed '{user_input}' to {dt}")
            return dt
            
        except Exception as e:
            logger.error(f"Failed to process Gemini response: {e}")
            return None
            
    except DateParsingError:
        # Re-raise DateParsingError as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in date parsing: {e}")
        raise DateParsingError(f"Unexpected error during date parsing: {e}")