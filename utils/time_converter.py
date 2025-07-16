from datetime import datetime
from zoneinfo import ZoneInfo

# sgt = ZoneInfo("Asia/Singapore")

def sgt_to_utc(time: datetime) -> datetime:
    return time.astimezone(ZoneInfo("UTC"))

def utc_to_sgt(time: datetime) -> datetime:
    return time.astimezone(ZoneInfo("Asia/Singapore"))