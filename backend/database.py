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

try:
    client = MongoClient(MONGO_URI, connectTimeoutMS=5000)
    # Ping to check if the connection is actually alive
    client.admin.command('ping')
    print("Connected to primary MongoDB successfully!")
except Exception as e:
    print(f"Primary MongoDB connection failed: {e}. Falling back to local MongoDB.")
    # Local fallback
    LOCAL_URI = "mongodb://localhost:27017"
    client = MongoClient(LOCAL_URI, connectTimeoutMS=5000)
    try:
        client.admin.command('ping')
        print("Connected to fallback local MongoDB successfully!")
    except Exception as local_err:
        print(f"Fallback MongoDB connection also failed: {local_err}")

db = client["knowledge_db"]

documents_collection = db["documents"]
topics_collection = db["important_topics"]
users_collection = db["users"]
assessments_collection = db["assessments"]
