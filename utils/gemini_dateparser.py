from config import GEMINI_API_KEY
from google import genai
from google.genai import types
from pydantic import BaseModel
from datetime import datetime, timezone
from utils.time_converter import utc_to_sgt
from zoneinfo import ZoneInfo

def gemini_dateparser(user_input):
    # Define variables
    now_utc = datetime.now(timezone.utc)
    now_sgt = utc_to_sgt(now_utc)

    # Step 1: Define schema
    class ParsedDate(BaseModel):
        sgt_datetime: datetime  # ISO 8601 string in UTC
        original_input: str

    # Step 2: Initialize Gemini client
    client = genai.Client(api_key=GEMINI_API_KEY)

    # Step 3: User input
    user_input = user_input

    # Step 4: Gemini content generation call
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

    # Step 5: Use the structured result
    parsed_result: ParsedDate = response.parsed

    # Check for error in Gemini
    if isinstance(parsed_result, type(None)):
        return None
    
    dt = parsed_result.sgt_datetime
    
    # Ensure it's timezone-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("Asia/Singapore"))

    return dt