from pymongo import MongoClient

def check_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["knowledge_db"]
    topics_col = db["topics"]
    docs_col = db["documents"]

    print(f"Total Documents: {docs_col.count_documents({})}")
    print(f"Total Topics: {topics_col.count_documents({})}")

    print("\nRecent Documents:")
    for doc in docs_col.find().sort("_id", -1).limit(3):
        print(f"- Title: {doc.get('title')}, Bytes: {doc.get('file_size')}, Content Length: {len(doc.get('content', ''))}")

    print("\nTopics in DB:")
    for t in topics_col.find():
        print(f"- Topic: {t['topic']}, Importance: {t['importance']}")

if __name__ == "__main__":
    check_db()
