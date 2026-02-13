from pymongo import MongoClient
from file_reader import read_document
import os

def test_reader():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["knowledge_db"]
    docs_col = db["documents"]

    doc = docs_col.find_one(sort=[("_id", -1)])
    if not doc:
        print("No document found in DB")
        return

    file_path = doc.get("file_path")
    print(f"Testing file: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"File not found on disk: {file_path}")
        return

    try:
        content = read_document(file_path)
        print(f"Extraction result length: {len(content)}")
        print("First 100 characters of content:")
        print(f"'{content[:100]}'")
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    test_reader()
