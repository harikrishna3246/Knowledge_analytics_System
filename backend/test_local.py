from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.database.command('ping')
    print("Successfully connected to Local MongoDB!")
except Exception as e:
    print(f"Failed to connect to Local MongoDB: {e}")
