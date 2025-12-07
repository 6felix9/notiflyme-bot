"""
Database connection utilities for MongoDB.

This module provides a centralized database connection manager
with connection pooling and reuse capabilities.
"""

from typing import Optional
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from config import MONGO_URI, DATABASE_NAME, REMINDERS_COLLECTION
from utils.logger import setup_logger

# Set up logging
logger = setup_logger(__name__)


class DatabaseManager:
    """
    Singleton database connection manager.
    
    Manages MongoDB connections with connection pooling and reuse.
    Ensures only one client instance is created per application.
    """
    
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None
    
    def __new__(cls) -> 'DatabaseManager':
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        if self._client is None:
            logger.info(f"Connecting to MongoDB at {MONGO_URI}")
            self._client = MongoClient(MONGO_URI)
            self._database = self._client[DATABASE_NAME]
            logger.info(f"Connected to database: {DATABASE_NAME}")
    
    @property
    def database(self) -> Database:
        """Get the database instance."""
        if self._database is None:
            raise RuntimeError("Database not initialized")
        return self._database
    
    @property
    def reminders_collection(self) -> Collection:
        """Get the reminders collection."""
        return self.database[REMINDERS_COLLECTION]
    
    def close(self) -> None:
        """Close the database connection."""
        if self._client:
            self._client.close()
            logger.info("Database connection closed")
            self._client = None
            self._database = None


# Global database manager instance
db_manager = DatabaseManager()


def get_database() -> Database:
    """
    Returns a MongoDB database instance.
    
    Uses the singleton DatabaseManager for connection pooling.
    
    Returns:
        Database: MongoDB database instance
    """
    return db_manager.database


def get_reminders_collection() -> Collection:
    """
    Returns the reminders collection.
    
    Returns:
        Collection: MongoDB reminders collection
    """
    return db_manager.reminders_collection

# User settings configuration
USERS_COLLECTION = "users"


def get_users_collection() -> Collection:
    """
    Returns the users collection.
    
    Returns:
        Collection: MongoDB users collection
    """
    return db_manager.database[USERS_COLLECTION]


def get_user_timezone(user_id: int) -> str:
    """
    Get user's timezone preference.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        str: User's timezone string, defaults to 'Asia/Singapore'
    """
    try:
        users = get_users_collection()
        user = users.find_one({"user_id": user_id})
        if user and "timezone" in user:
            return user["timezone"]
    except Exception as e:
        logger.error(f"Error fetching user timezone: {e}")
        
    return "Asia/Singapore"  # Default fallback


def set_user_timezone(user_id: int, tz_string: str) -> bool:
    """
    Set user's timezone preference.
    
    Args:
        user_id: Telegram user ID
        tz_string: Timezone string to set
        
    Returns:
        bool: True if successful
    """
    try:
        users = get_users_collection()
        users.update_one(
            {"user_id": user_id},
            {"$set": {
                "timezone": tz_string, 
                "updated_at": datetime.now(timezone.utc)
            }},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error setting user timezone: {e}")
        return False


# Optional: Test connection when the script runs
if __name__ == "__main__":
    db = get_database()
    logger.info(f"Connected to MongoDB database: {db.name}")
