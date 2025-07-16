"""
Database connection utilities for MongoDB.

This module provides a centralized database connection manager
with connection pooling and reuse capabilities.
"""

from typing import Optional
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

# Optional: Test connection when the script runs
if __name__ == "__main__":
    db = get_database()
    logger.info(f"Connected to MongoDB database: {db.name}")
