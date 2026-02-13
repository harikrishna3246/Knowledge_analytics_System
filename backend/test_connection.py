from database import documents_collection
import pymongo

try:
    # distinct is a simple command to check connection
    documents_collection.database.command('ping')
    print("Successfully connected to MongoDB Atlas!")
    print(f"Database: {documents_collection.database.name}")
    print(f"Collection: {documents_collection.name}")
except Exception as e:
    print(f"failed to connect: {e}")
