# 🧠 KnowledgeAI: Intelligent Knowledge Analytics System

KnowledgeAI is a state-of-the-art, AI-powered platform designed to transform static documents into interactive knowledge maps. It helps students, researchers, and professionals analyze complex data, extract key insights, and test their understanding through AI-generated assessments—all within a premium, feature-rich interface.

---

## 🚀 Key Features

### 1. **Intelligent Document Parsing**
*   **Multi-Format Support**: Upload PDF and DOCX files.
*   **Deep Content Extraction**: Automatically splits documents into paragraphs and sentences for granular analysis.
*   **Knowledge Graphing**: Identifies key topics, definitions, and themes using NLP and AI logic.

### 2. **AI-Driven Topic Insights**
*   **Deep-Dive Analysis**: For every extracted topic, the system generates:
    *   **Contextual Extracts**: Precise points taken directly from your document.
    *   **Academic Knowledge**: Fundamental explanations provided by the base AI model.
    *   **Real-World Application**: Practical examples of the concept in action.
*   **Custom Note Export**: Generate professional PDF study notes for any topic with one click.

### 3. **Smart Learning Tools**
*   **Tutor AI Assistant**: Chat with a specialized AI bot for every specific topic to clarify doubts in real-time.
*   **Personalized Quizzes**: Automatically generate MCQs and problem-solving questions based on your specific document.
*   **Assessment History**: Track your scores and progress over time on your dashboard.

### 4. **Premium Security & UI**
*   **Hybrid Authentication**: Support for both custom Email/Password login and one-tap Google OAuth.
*   **Session Guard**: Enhanced security that ensures the system starts at the Login page for every new browser session.
*   **Stunning Aesthetics**: A modern, glassmorphic UI with smooth animations, curated palettes, and a dedicated User Dashboard.

---

## 🏗️ Technology Stack

### **Frontend**
*   **Framework**: React.js (v19)
*   **Styling**: Vanilla CSS3 (Custom Design System with Glassmorphism)
*   **Navigation**: React Router Dom
*   **Icons**: React Icons (FontAwesome)
*   **Authentication**: Google OAuth for React (@react-oauth/google)
*   **Data Handling**: JWT-decode for secure token management

### **Backend**
*   **Language**: Python 3.10+
*   **Framework**: FastAPI (High-performance web API)
*   **AI Engine**: Groq LPU (Llama 3 / Mixtral Models)
*   **Database**: MongoDB Atlas (Cloud NoSQL)
*   **PDF Logic**: ReportLab (Professional PDF generation)
*   **NLP Tools**: NLTK (Bigram extraction and text cleaning)
*   **Security**: JWT (JSON Web Tokens) with Python-jose/PyJWT

---

## 🛠️ Project Development Journey: From Start to Finish

### **Phase 1: Foundation (Backend Core)**
*   Built the FastAPI server and integrated MongoDB Atlas for persistent storage.
*   Implemented file reading logic for PDF/DOCX using custom harvesters.
*   Created the **Knowledge Extraction Engine** using Groq API to pull bigrams and priorities.

### **Phase 2: Authentication & Social Login**
*   Developed a secure Login/Signup system with JWT tokenization.
*   Integrated **Google One-Tap Authentication** for a seamless user experience.
*   Implemented "Remember Me" functionality for email persistence.

### **Phase 3: Interactive Learning Modules**
*   Built the **Topic Insights** page to display structured knowledge cards.
*   Added the **Tutor Chat** popup allowing users to ask questions about specific topics.
*   Developed the **Quiz Engine** that generates 10 unique questions per topic and stores history.

### **Phase 4: UI/UX Master-Polish**
*   Conducted a complete **Dashboard UI Refresh**, creating a premium, clean aesthetic with better font-families (Outfit, Outfit, Inter).
*   Added glassmorphic containers, hover animations, and a responsive grid layout.
*   Fixed routing to prioritize the Login Page as the entry point for all new visits.
*   Secured data by switching critical authentication tokens to `sessionStorage`.

---

## ⚙️ Setup Instructions

### **Prerequisites**
*   Python 3.10+ and Node.js installed.
*   A MongoDB Atlas cluster and a Groq API Key.

### **1. Backend Setup**
1. Navigate to `backend/`:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/Scripts/activate # Windows
   ```
3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pymongo python-dotenv certifi dnspython pyjwt groq reportlab nltk
   ```
4. Create a `.env` file in `backend/` with:
   ```env
   MONGODB_URI=your_atlas_connection_string
   GROQ_API_KEY=your_groq_key
   JWT_SECRET=your_jwt_secret
   ```
5. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

### **2. Frontend Setup**
1. Navigate to `frontend/`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in `frontend/` with:
   ```env
   REACT_APP_GOOGLE_CLIENT_ID=your_google_client_id
   ```
4. Run the development server:
   ```bash
   npm start
   ```

---

## 📊 Database Schema (MongoDB Atlas)
*   **Users**: Profile data and authentication.
*   **Documents**: Stored metadata, hashes, and full text extracts.
*   **Important Topics**: Extracted concepts with academic insights and examples.
*   **Assessments**: Quiz scores and history tied to user accounts.

---

**KnowledgeAI System** – *Bridging the gap between raw data and true understanding.* 🚀
