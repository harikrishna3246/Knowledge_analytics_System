from dotenv import load_dotenv
import os

# Load env before other imports
load_dotenv(override=True)

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
from pydantic import BaseModel
from groq_chat import topic_chat

from file_reader import read_document, get_file_hash
from topic_extractor import extract_topics
from topic_content_extractor import extract_topic_content
from external_content_generator import generate_external_content
from assessment_generator import generate_topic_quiz
from database import documents_collection, topics_collection
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import tempfile
import os

app = FastAPI()

# Add CORS Middleware to allow requests from React (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize_text(item):
    """Ensures AI-provided content is a string, even if it returns structured objects."""
    if not item: return ""
    if isinstance(item, str): return item
    if isinstance(item, list):
        return [normalize_text(i) for i in item]
    if isinstance(item, dict):
        # Extract common keys or join all strings
        text = item.get("description") or item.get("point") or item.get("importance") or item.get("explanation") or item.get("text")
        if text: return str(text)
        return ": ".join([str(v) for v in item.values() if isinstance(v, (str, int, float))])
    return str(item)


@app.get("/")
def root():
    return {"status": "Server is running"}

@app.get("/mongo-test")
def mongo_test():
    return {"message": "MongoDB connected successfully"}

@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...), subject: str = Form(...)):
    try:
        from datetime import datetime
        import json
        from groq_client import client
        
        if not subject or not subject.strip():
            return {"error": "Subject name is mandatory. Please provide a subject."}

        # Create 'documents' directory if it doesn't exist
        os.makedirs("documents", exist_ok=True)
        
        file_path = f"documents/{file.filename}"
        
        # Save file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 1. Generate Document Hash
        file_hash = get_file_hash(file_path)
        
        # 2. Check if document already exists WITH THIS SUBJECT
        existing_doc = documents_collection.find_one({"hash": file_hash, "subject": subject})
        if existing_doc:
            # Update timestamp to make it the "latest" document
            documents_collection.update_one({"_id": existing_doc["_id"]}, {"$set": {"uploaded_at": datetime.utcnow()}})
            return {
                "message": f"Document already processed for {subject}",
                "filename": file.filename,
                "document_id": str(existing_doc["_id"]),
                "already_exists": True
            }

        # 3. Extract document content and headings
        try:
            content, headings = read_document(file_path)
        except Exception as e:
            content = f"[Content extraction failed: {str(e)}]"
            headings = []

        # 4. VALIDATE SUBJECT VS DOCUMENT (AI-based consistency check)
        validation_preview = content[:5000]
        validation_prompt = f"""
        Analyze the following text and determine if it belongs to the subject: '{subject}'.
        
        TEXT PREVIEW:
        {validation_preview}
        
        Instruction:
        - If the content is significantly related to '{subject}', return {{"match": true}}.
        - If the content has NOTHING to do with '{subject}', return {{"match": false, "reason": "Short explanation why it doesn't match"}}.
        
        OUTPUT FORMAT (STRICT JSON ONLY):
        {{"match": boolean, "reason": "string"}}
        """
        
        try:
            val_response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": validation_prompt}],
                response_format={"type": "json_object"}
            )
            val_result = json.loads(val_response.choices[0].message.content)
            
            if not val_result.get("match", False):
                # Remove file if it doesn't match
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    "error": f"Invalid Document: The content does not match the subject '{subject}'. {val_result.get('reason', '')}",
                    "status_code": 400
                }
        except Exception as e:
            print(f"Validation Error: {e}")

        # Get file size
        file_size = os.path.getsize(file_path)
        
        # 5. Store complete document data in MongoDB
        document = {
            "title": file.filename,
            "subject": subject,
            "hash": file_hash,
            "file_path": file_path,
            "content_type": file.content_type,
            "file_size": file_size,
            "content": content,
            "headings": headings,
            "uploaded_at": datetime.utcnow()
        }
        result = documents_collection.insert_one(document)
        
        return {
            "message": "Document uploaded and verified successfully",
            "filename": file.filename,
            "file_size": f"{file_size / 1024:.2f} KB",
            "content_preview": content[:200] + "..." if len(content) > 200 else content,
            "document_id": str(result.inserted_id),
            "already_exists": False
        }
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}



@app.get("/get-documents")
def get_documents():
    """Get all uploaded documents from MongoDB"""
    try:
        documents = list(documents_collection.find())
        
        # Convert ObjectId to string and format response
        result = []
        for doc in documents:
            result.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", "Unknown"),
                "file_size": doc.get("file_size", 0),
                "content_type": doc.get("content_type", "Unknown"),
                "uploaded_at": doc.get("uploaded_at", "Unknown"),
                "content_preview": doc.get("content", "")[:200] + "..." if len(doc.get("content", "")) > 200 else doc.get("content", "")
            })
        
        return {
            "total_documents": len(result),
            "documents": result
        }
    except Exception as e:
        return {"error": f"Failed to fetch documents: {str(e)}"}


@app.get("/read-document")
def read_uploaded_document():
    # Get the most recent document
    document = documents_collection.find_one(sort=[("_id", -1)])
    if not document:
        return {"error": "No document found"}

    # Handle case where file_path might be missing in older documents
    if "file_path" not in document:
        return {"error": "Document found but has no file_path"}

    file_path = document["file_path"]
    try:
        content, headings = read_document(file_path)
        return {
            "message": "Document content extracted successfully",
            "content_preview": content[:1000]
        }
    except Exception as e:
        return {"error": f"Failed to read document: {str(e)}"}


@app.get("/get-stored-topics")
def get_stored_topics():
    """Retrieve topics ONLY for the most recently uploaded/selected document"""
    try:
        # Find the latest document by upload time
        latest_doc = documents_collection.find_one(sort=[("uploaded_at", -1)])
        if not latest_doc:
            return []
            
        topics = list(topics_collection.find({"document_id": latest_doc["_id"]}))
        results = []
        for t in topics:
            t["_id"] = str(t["_id"])
            t["document_id"] = str(t["document_id"])
            results.append(t)
        return results
    except Exception as e:
        return {"error": f"Failed to fetch topics: {str(e)}"}

@app.get("/extract-topics")
def extract_document_topics():
    # Find the latest document by upload time
    document = documents_collection.find_one(sort=[("uploaded_at", -1)])
    if not document:
        return {"error": "No document found"}

    content = document.get("content", "")
    subject = document.get("subject", "General")
    headings = document.get("headings", [])

    topics = extract_topics(content, subject=subject, headings=headings)

    return {
        "message": "Important topics extracted successfully",
        "topics": topics
    }

@app.post("/store-topics-with-content")
def store_topics_with_content():
    # Find the latest document by upload time
    document = documents_collection.find_one(sort=[("uploaded_at", -1)])
    if not document:
        return {"error": "No document found"}

    # 1. CHECK IF TOPICS ALREADY EXIST FOR THIS DOCUMENT HASH
    # If the document was found by hash in upload, it might already have topics
    existing_topics = list(topics_collection.find({"document_id": document["_id"]}))
    if existing_topics:
        # Format for response
        for t in existing_topics:
            t["_id"] = str(t["_id"])
            t["document_id"] = str(t["document_id"])
        return {
            "message": "Retrieving existing topics for this document",
            "topics": existing_topics
        }

    # 2. CLEAR PREVIOUS topics (only if we want to reset every time, 
    # but since we checking hash above, we only clear if no topics found for this doc)
    # Actually, the user wants "topics are changing if i again upload the same document it should not occur"
    # So we should NOT clear if they are for a DIFFERENT document.
    # But usually this system only cares about the current active document.
    # To keep it safe, let's only clear if we are reprocessing.
    
    # topics_collection.delete_many({}) # Removed this to allow persistence

    content = document.get("content", "")
    subject = document.get("subject", "General")
    headings = document.get("headings", [])

    topics = extract_topics(content, subject=subject, headings=headings)
    # LIMIT to prevent connection timeout during AI generation
    topics = topics[:15]

    stored_topics = []

    for topic_data in topics:
        topic_name = topic_data["topic"]
        priority = topic_data["priority"]
        reason = topic_data["reason"]

        try:
            # Content from document
            doc_content = extract_topic_content(content, topic_name)
            
            # Hybrid Content from external knowledge
            try:
                hybrid_content = generate_external_content(topic_name)
            except Exception as e:
                print(f"Error generating content for {topic_name}: {e}")
                hybrid_content = {"academic_knowledge": [], "real_world_example": "Content unavailable due to AI error."}

            topic_record = {
                "document_id": document["_id"],
                "topic": topic_name,
                "priority": priority,
                "reason": reason,
                "from_document": normalize_text(doc_content),
                "academic_knowledge": normalize_text(hybrid_content.get("academic_knowledge", [])),
                "real_world_example": normalize_text(hybrid_content.get("real_world_example", "")),
                "assessment": [] 
            }
    
            topics_collection.insert_one(topic_record)
            
            # Format for response
            topic_record["_id"] = str(topic_record["_id"])
            topic_record["document_id"] = str(topic_record["document_id"])
            stored_topics.append(topic_record)
            
        except Exception as e:
            print(f"Skipping topic {topic_name} due to error: {e}")
            continue

    return {
        "message": f"Academic topics for {subject} stored",
        "topics": stored_topics
    }

@app.get("/download-topic-pdf/{topic_name}")
def download_topic_pdf(topic_name: str):
    topic = topics_collection.find_one({"topic": topic_name})
    if not topic:
        return {"error": "Topic not found"}

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=A4)

    width, height = A4
    y = height - 50

    # Topic Title (Bold)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Academic Insight: {topic['topic'].title()}")

    y -= 25
    c.setFont("Helvetica", 12)
    c.drawString(50, y, f"Priority: {topic['priority']} | Reason: {topic['reason']}")

    # 1. Document Extracts
    y -= 40
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Contextual Points from Document:")
    
    y -= 20
    c.setFont("Helvetica", 11)
    for point in topic.get("from_document", []):
        point_str = normalize_text(point)
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {point_str[:90]}...")
        y -= 18

    # 2. Academic Knowledge
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Fundamental Academic Knowledge:")

    y -= 20
    c.setFont("Helvetica", 11)
    for point in topic.get("academic_knowledge", []):
        point_str = normalize_text(point)
        if y < 80:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 11)
        c.drawString(60, y, f"• {point_str}")
        y -= 18

    # 3. Real-world Example
    y -= 20
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, y, "Real-world Application:")

    y -= 20
    c.setFont("Helvetica", 11)
    example = normalize_text(topic.get("real_world_example", "N/A"))
    # Wrap text manually for the example
    c.drawString(60, y, f"• {example[:90]}")
    if len(example) > 90:
        y -= 15
        c.drawString(60, y, f"  {example[90:180]}")

    c.save()
    return FileResponse(temp_file.name, media_type="application/pdf", filename=f"{topic_name}_notes.pdf")

# Keeping the old download-topic for backward compatibility if needed, 
# but recommendation is to use PDF.
@app.get("/download-topic/{topic_name}")
def download_topic(topic_name: str):
    topic = topics_collection.find_one({"topic": topic_name})
    if not topic:
        return {"error": "Topic not found"}

    content = f"""
Topic: {topic['topic']}
Priority: {topic['priority']}
Reason: {topic['reason']}

Contextual Points from Document:
{'\n'.join([f"• {normalize_text(p)}" for p in topic.get('from_document', [])])}

Fundamental Academic Knowledge:
{'\n'.join([f"• {normalize_text(p)}" for p in topic.get('academic_knowledge', [])])}

Real-world Application:
• {normalize_text(topic.get('real_world_example', 'N/A'))}
"""

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    temp_file.write(content.encode("utf-8"))
    temp_file.close()

    return FileResponse(
        temp_file.name,
        media_type="text/plain",
        filename=f"{topic_name}_notes.txt"
    )

class ChatRequest(BaseModel):
    topic: str
    question: str
    document_context: str = ""

@app.post("/chat")
def chat_with_topic(data: ChatRequest):
    answer = topic_chat(
        topic=data.topic,
        question=data.question,
        document_context=data.document_context
    )
    return {"answer": answer}

@app.post("/generate-quiz")
def generate_quiz_endpoint(data: dict):
    topic = data.get("topic")
    if not topic:
        return {"error": "Topic is required"}
    return generate_topic_quiz(topic)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
