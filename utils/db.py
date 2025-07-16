import os
from pymongo import MongoClient

def get_database():
    """
    Returns a MongoDB database instance.
    """
    # Get connection string from environment or default to localhost
    connection_string = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    client = MongoClient(connection_string)
    db = client["telegram"]
    return db

# Optional: Test connection when the script runs
if __name__ == "__main__":
    db = get_database()
    print("Connected to MongoDB:", db.name)
