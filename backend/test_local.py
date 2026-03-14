import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env from backend so this script works when run from any CWD
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Use Atlas URI when provided, otherwise fall back to localhost
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
