"""
Time conversion utilities for timezone handling.

This module provides functions to convert between Singapore Time (SGT) 
and Coordinated Universal Time (UTC).
"""

from datetime import datetime
from zoneinfo import ZoneInfo


def sgt_to_utc(time: datetime) -> datetime:
    """
    Convert Singapore Time to UTC.
    
    Args:
        time: A datetime object in Singapore timezone
        
    Returns:
        datetime: The equivalent time in UTC timezone
    """
    return time.astimezone(ZoneInfo("UTC"))


def utc_to_sgt(time: datetime) -> datetime:
    """
    Convert UTC to Singapore Time.
    
    Args:
        time: A datetime object in UTC timezone
        
    Returns:
        datetime: The equivalent time in Singapore timezone
    """
    return time.astimezone(ZoneInfo("Asia/Singapore"))