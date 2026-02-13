import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI")
# MongoClient configuration - local usually doesn't need TLS
client = MongoClient(MONGO_URI, connectTimeoutMS=5000)
db = client["knowledge_db"]

documents_collection = db["documents"]
topics_collection = db["important_topics"]
