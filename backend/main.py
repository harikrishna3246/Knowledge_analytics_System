from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load env before other imports
load_dotenv(override=True)

import jwt
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import shutil
import os
from typing import Optional
from pydantic import BaseModel
from groq_chat import topic_chat

from file_reader import read_document, get_file_hash
from topic_extractor import extract_topics
from topic_content_extractor import extract_topic_content
from external_content_generator import generate_external_content
from assessment_generator import generate_topic_quiz
from database import documents_collection, topics_collection, users_collection, assessments_collection
from fastapi.responses import FileResponse, JSONResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
import tempfile
import os

import traceback

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    print("Unhandled exception:", exc)
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": str(exc)})

# Add CORS Middleware to allow requests from React
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT-based auth configuration
JWT_SECRET = os.getenv("JWT_SECRET", "1f9589992df49905725323cf6a326caf858179f4cc51137842bb56423f5be723")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


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
    try:
        # Quick ping to ensure MongoDB connection is working
        documents_collection.database.client.admin.command('ping')
        return {"message": "MongoDB connected successfully"}
    except Exception as e:
        return {"error": "MongoDB connection failed", "details": str(e)}

class LoginRequest(BaseModel):
    email: str
    password: str = ""
    name: str = ""
    picture: str = ""

class SignupRequest(BaseModel):
    email: str
    password: str
    name: str = ""
    picture: str = ""

@app.post("/signup")
def signup_user(data: SignupRequest):
    print("DEBUG: /signup called with", data)
    from datetime import datetime
    try:
        user = users_collection.find_one({"email": data.email})
        if user:
            return {"error": "Email already registered"}

        now = datetime.utcnow()
        result = users_collection.insert_one({
            "email": data.email,
            "password": data.password, # Note: In production, password should be hashed
            "name": data.name,
            "picture": data.picture,
            "created_at": now,
            "last_login": now
        })

        token = create_access_token({"sub": data.email, "user_id": str(result.inserted_id)})
        return {"message": "Signup successful", "email": data.email, "token": token}
    except Exception as e:
        # Log server-side for debugging
        print("Signup error:", e)
        return {"error": f"Signup failed: {e}"}

@app.post("/login")
def login_user(data: LoginRequest):
    from datetime import datetime
    user = users_collection.find_one({"email": data.email})
    
    if data.password:
        # Standard login
        if not user or user.get("password") != data.password:
            return {"error": "Invalid email or password"}
        
        users_collection.update_one(
            {"email": data.email},
            {"$set": {"last_login": datetime.utcnow()}}
        )
    else:
        # Google login (no password provided)
        if not user:
            users_collection.insert_one({
                "email": data.email,
                "name": data.name,
                "picture": data.picture,
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            })
        else:
            update_data = {"last_login": datetime.utcnow()}
            if data.name:
                update_data["name"] = data.name
            if data.picture:
                update_data["picture"] = data.picture
            
            users_collection.update_one(
                {"email": data.email},
                {"$set": update_data}
            )

    token = create_access_token({"sub": data.email})
    return {"message": "Login successful", "email": data.email, "token": token}

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    subject: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
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

        # 2. Check if document already exists WITH THIS SUBJECT for this user
        existing_doc = documents_collection.find_one({
            "hash": file_hash,
            "subject": subject,
            "user_email": current_user.get("email")
        })
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

        # Get file size
        file_size = os.path.getsize(file_path)
        
        # 5. Store complete document data in MongoDB
        document = {
            "title": file.filename,
            "subject": subject,
            "hash": file_hash,
            "user_email": current_user.get("email"),
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
def get_documents(current_user: dict = Depends(get_current_user)):
    """Get all uploaded documents for the current user"""
    try:
        # Return docs for this user (fallback to public docs if they exist)
        query = {"$or": [{"user_email": current_user.get("email")}, {"user_email": {"$exists": False}}]}
        documents = list(documents_collection.find(query).sort("uploaded_at", -1))
        
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
def read_uploaded_document(current_user: dict = Depends(get_current_user)):
    # Get the most recent document for this user
    document = documents_collection.find_one(
        {"user_email": current_user.get("email")},
        sort=[("uploaded_at", -1)]
    )
    if not document:
        # Fallback to any document if user has none (legacy behavior)
        document = documents_collection.find_one(sort=[("uploaded_at", -1)])
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


from bson import ObjectId

@app.get("/get-stored-topics")
def get_stored_topics(document_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    """Retrieve topics for the optionally provided document_id, or the most recently uploaded document for this user"""
    try:
        target_doc = None
        if document_id:
            target_doc = documents_collection.find_one({
                "_id": ObjectId(document_id),
                "user_email": current_user.get("email")
            })
            if not target_doc:
                return []
        
        if not target_doc:
            # Find the latest document by upload time for this user
            target_doc = documents_collection.find_one(
                {"user_email": current_user.get("email")},
                sort=[("uploaded_at", -1)]
            )
            if not target_doc:
                # Fallback to any document if user has none (legacy behavior)
                target_doc = documents_collection.find_one(sort=[("uploaded_at", -1)])
                
        if not target_doc:
            return []
            
        topics = list(topics_collection.find({
            "document_id": target_doc["_id"],
            "user_email": current_user.get("email")
        }))
        if not topics:
            # fallback to legacy topics without user_email
            topics = list(topics_collection.find({"document_id": target_doc["_id"]}))

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
def store_topics_with_content(document_id: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    from bson import ObjectId
    document = None
    
    if document_id:
        document = documents_collection.find_one({
            "_id": ObjectId(document_id),
            "user_email": current_user.get("email")
        })
        
    if not document:
        # Find the latest document by upload time for this user
        document = documents_collection.find_one(
            {"user_email": current_user.get("email")},
            sort=[("uploaded_at", -1)]
        )
    if not document:
        # Fallback to any document if user has none (legacy behavior)
        document = documents_collection.find_one(sort=[("uploaded_at", -1)])
    if not document:
        return {"error": "No document found"}

    # 1. CHECK IF TOPICS ALREADY EXIST FOR THIS DOCUMENT HASH
    # If the document was found by hash in upload, it might already have topics
    existing_topics = list(topics_collection.find({
        "document_id": document["_id"],
        "user_email": current_user.get("email")
    }))
    if not existing_topics:
        # fallback to legacy topics without user_email
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
                "user_email": current_user.get("email"),
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
def download_topic_pdf(topic_name: str, current_user: dict = Depends(get_current_user)):
    topic = topics_collection.find_one({"topic": topic_name, "user_email": current_user.get("email")})
    if not topic:
        return {"error": "Topic not found"}

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp_file.close()

    # Create document template with proper margins
    doc = SimpleDocTemplate(
        temp_file.name, 
        pagesize=A4, 
        rightMargin=50, 
        leftMargin=50, 
        topMargin=50, 
        bottomMargin=50
    )
    styles = getSampleStyleSheet()
    
    # Custom Professional Styles
    title_style = ParagraphStyle(
        'TopicTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=15,
        textColor=colors.HexColor("#2c2420"),
        alignment=TA_LEFT
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.gray,
        spaceAfter=15
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor("#d6b496"),
        borderPadding=(0, 0, 2, 0)
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=10,
        alignment=TA_LEFT
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(f"Academic Insight: {topic['topic'].title()}", title_style))
    story.append(Paragraph(f"Priority: {topic.get('priority', 'N/A')} | Reason: {topic.get('reason', 'N/A')}", subtitle_style))
    story.append(Spacer(1, 15))

    # 1. Document Extracts
    story.append(Paragraph("Contextual Points from Document", heading_style))
    doc_points = topic.get("from_document", [])
    if isinstance(doc_points, str):
        # If it was saved as a single string instead of list
        doc_points = [doc_points]
    
    for point in doc_points:
        point_str = normalize_text(point)
        if point_str.strip():
            story.append(Paragraph(f"<b>&bull;</b> {point_str}", body_style))

    # 2. Academic Knowledge
    story.append(Paragraph("Fundamental Academic Knowledge", heading_style))
    academic_points = topic.get("academic_knowledge", [])
    if isinstance(academic_points, str):
        academic_points = [academic_points]
    
    for point in academic_points:
        point_str = normalize_text(point)
        if point_str.strip():
            story.append(Paragraph(f"<b>&bull;</b> {point_str}", body_style))

    # 3. Real-world Example
    story.append(Paragraph("Real-world Application", heading_style))
    example = normalize_text(topic.get("real_world_example", "N/A"))
    story.append(Paragraph(f"<b>&bull;</b> {example}", body_style))

    # Build PDF with automatic page breaking
    doc.build(story)
    
    return FileResponse(temp_file.name, media_type="application/pdf", filename=f"{topic_name}_notes.pdf")

# Keeping the old download-topic for backward compatibility if needed, 
# but recommendation is to use PDF.
@app.get("/download-topic/{topic_name}")
def download_topic(topic_name: str, current_user: dict = Depends(get_current_user)):
    topic = topics_collection.find_one({"topic": topic_name, "user_email": current_user.get("email")})
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
def chat_with_topic(data: ChatRequest, current_user: dict = Depends(get_current_user)):
    answer = topic_chat(
        topic=data.topic,
        question=data.question,
        document_context=data.document_context
    )
    return {"answer": answer}

@app.post("/generate-quiz")
def generate_quiz_endpoint(data: dict, current_user: dict = Depends(get_current_user)):
    topic = data.get("topic")
    if not topic:
        return {"error": "Topic is required"}
    return generate_topic_quiz(topic)

class SaveAssessmentRequest(BaseModel):
    topic: str
    score: int
    total: int
    percentage: int

@app.post("/save-assessment")
def save_assessment(data: SaveAssessmentRequest, current_user: dict = Depends(get_current_user)):
    try:
        assessments_collection.insert_one({
            "user_email": current_user.get("email"),
            "topic": data.topic,
            "score": data.score,
            "total": data.total,
            "percentage": data.percentage,
            "completed_at": datetime.utcnow()
        })
        return {"message": "Assessment saved successfully"}
    except Exception as e:
        return {"error": f"Failed to save assessment: {str(e)}"}

@app.get("/user-dashboard")
def get_user_dashboard(current_user: dict = Depends(get_current_user)):
    try:
        user_info = {
            "name": current_user.get("name", ""),
            "email": current_user.get("email", ""),
            "picture": current_user.get("picture", "")
        }

        # Fetch recent documents
        recent_docs = list(documents_collection.find(
            {"user_email": current_user.get("email")}
        ).sort("uploaded_at", -1).limit(10))

        docs_formatted = []
        for doc in recent_docs:
            # Fetch topics for this document
            doc_topics = list(topics_collection.find({
                "document_id": doc["_id"],
                "user_email": current_user.get("email")
            }))
            if not doc_topics:
                doc_topics = list(topics_collection.find({"document_id": doc["_id"]}))
                
            topics_formatted = [{"topic": t.get("topic", "Unknown"), "priority": t.get("priority", "N/A")} for t in doc_topics]
                
            docs_formatted.append({
                "id": str(doc["_id"]),
                "title": doc.get("title", "Unknown"),
                "subject": doc.get("subject", ""),
                "uploaded_at": doc.get("uploaded_at").isoformat() if doc.get("uploaded_at") else "",
                "topics": topics_formatted
            })

        # Fetch recent assessments
        recent_assessments = list(assessments_collection.find(
            {"user_email": current_user.get("email")}
        ).sort("completed_at", -1).limit(10))

        assessments_formatted = []
        for a in recent_assessments:
            assessments_formatted.append({
                "id": str(a["_id"]),
                "topic": a.get("topic", "Unknown"),
                "score": a.get("score", 0),
                "total": a.get("total", 0),
                "percentage": a.get("percentage", 0),
                "completed_at": a.get("completed_at").isoformat() if a.get("completed_at") else ""
            })

        return {
            "user": user_info,
            "documents": docs_formatted,
            "assessments": assessments_formatted
        }
    except Exception as e:
        return {"error": f"Failed to fetch dashboard data: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
