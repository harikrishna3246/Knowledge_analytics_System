import os
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

# Ensure .env is loaded from the backend folder regardless of current working dir
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# Fallback to local MongoDB if env var is missing
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
print("DEBUG: Using MongoDB URI:", MONGO_URI)
# MongoClient configuration - local usually doesn't need TLS
client = MongoClient(MONGO_URI, connectTimeoutMS=5000)
db = client["knowledge_db"]

documents_collection = db["documents"]
topics_collection = db["important_topics"]
users_collection = db["users"]
