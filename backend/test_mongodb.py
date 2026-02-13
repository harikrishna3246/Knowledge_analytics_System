"""
MongoDB Connection Test Script
Run this to verify MongoDB Atlas connection is working
"""
from database import client, db, documents_collection

def test_connection():
    try:
        # Test connection
        client.admin.command('ping')
        print("✅ MongoDB connected successfully!")
        
        # Show database info
        print(f"\n📊 Database: {db.name}")
        print(f"📁 Collection: {documents_collection.name}")
        
        # Count documents
        count = documents_collection.count_documents({})
        print(f"📄 Total documents: {count}")
        
        # Show sample document if exists
        if count > 0:
            print("\n📝 Sample document:")
            sample = documents_collection.find_one()
            for key, value in sample.items():
                if key == "_id":
                    print(f"  {key}: {value}")
                elif key == "content":
                    # Show only first 100 chars of content
                    print(f"  {key}: {str(value)[:100]}...")
                else:
                    print(f"  {key}: {value}")
        else:
            print("\n⚠️ No documents found in collection")
            
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
