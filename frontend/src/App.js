import React, { useState, useEffect } from "react";
import "./App.css";
import { FaRocket, FaFilePdf, FaRobot, FaUpload, FaCheckCircle, FaExclamationTriangle, FaChartLine } from "react-icons/fa";
import { Routes, Route, Link, useNavigate, useLocation } from "react-router-dom";
import TopicInsights from "./components/TopicInsights";
import QuizPage from "./components/QuizPage";
import ResultPage from "./components/ResultPage";

function App() {
  const navigate = useNavigate();
  const location = useLocation();
  const [file, setFile] = useState(null);
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 50) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMessage("");
  };

  const uploadDocument = async () => {
    if (!file) {
      setMessage("⚠️ Please select a file first.");
      return;
    }
    if (!subject.trim()) {
      setMessage("⚠️ Please enter a subject name (e.g., DSA, OS) before uploading.");
      setIsUploading(false); // Ensure it's not stuck in uploading state
      return;
    }

    setIsUploading(true);
    setMessage("🚀 Uploading document...");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("subject", subject);

    try {
      // 1. Upload Document
      const uploadResponse = await fetch("http://127.0.0.1:8000/upload-document", {
        method: "POST",
        body: formData,
      });

      const uploadData = await uploadResponse.json();
      if (!uploadResponse.ok) throw new Error(uploadData.error || "Upload failed");

      // 2. Automatically Trigger Knowledge Analysis
      setMessage(`🧠 Analyzing document content for ${subject}...`);

      const analysisResponse = await fetch("http://127.0.0.1:8000/store-topics-with-content", {
        method: "POST",
      });

      if (!analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        throw new Error(analysisData.error || "Analysis failed");
      }

      setMessage("✅ Success! Knowledge base updated. Redirecting to insights...");

      // 3. Redirect after a short delay
      setTimeout(() => {
        navigate("/topics");
        setIsUploading(false);
      }, 2000);

    } catch (error) {
      console.error("Error:", error);
      setMessage(`❌ Error: ${error.message}`);
      setIsUploading(false);
    }
  };

  const isAssessment = location.pathname.startsWith("/quiz") || location.pathname === "/result";

  return (
    <div className="app-container">
      {/* Navbar */}
      {!isAssessment && (
        <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
          <div className="logo" onClick={() => navigate("/")} style={{ cursor: "pointer" }}>
            <img src="/assets/logo.png" alt="KnowledgeAI Logo" className="logo-img" />
            <span>KnowledgeAI</span>
          </div>
          <div className="nav-links">
            <Link to="/">Home</Link>
            <Link to="/topics">Insights</Link>
            <a href="#features">Features</a>
            <a href="#upload" className="cta-btn">Get Started</a>
          </div>
        </nav>
      )}

      <Routes>
        <Route path="/" element={
          <MainContent
            file={file}
            setFile={setFile}
            subject={subject}
            setSubject={setSubject}
            handleFileChange={handleFileChange}
            uploadDocument={uploadDocument}
            isUploading={isUploading}
            message={message}
            navigate={navigate}
          />
        } />
        <Route path="/topics" element={<TopicInsights />} />
        <Route path="/quiz/:topic" element={<QuizPage />} />
        <Route path="/result" element={<ResultPage />} />
      </Routes>

      {/* Footer */}
      {!isAssessment && (
        <footer className="footer">
          <p>&copy; 2024 KnowledgeAI System. All rights reserved.</p>
        </footer>
      )}
    </div>
  );
}

function MainContent({ file, setFile, subject, setSubject, handleFileChange, uploadDocument, isUploading, message, navigate }) {
  return (
    <main className="main-content">
      {/* Decorative Lines and Shapes */}
      <div className="decorative-bg">
        <div className="shape s1"></div>
        <div className="shape s2"></div>
        <svg className="bg-line-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
          <path d="M0,50 Q25,30 50,50 T100,50" fill="none" stroke="rgba(214, 180, 150, 0.2)" strokeWidth="0.5" />
        </svg>
      </div>
      {/* Hero Section */}
      <section id="home" className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">
            Unlock the Power of <br />
            <span className="gradient-text">AI Knowledge</span>
          </h1>
          <p className="hero-subtitle">
            Transform your documents into intelligent conversations.
            Upload PDFs, ask questions, and get instant answers powered by advanced AI.
          </p>
          <div className="hero-buttons">
            <a href="#upload" className="primary-btn">Analyze Document <FaRocket /></a>
            <button onClick={() => navigate("/topics")} className="secondary-btn">View Insights <FaChartLine /></button>
          </div>
        </div>
        <div className="hero-visual">
          <div className="visual-circle"></div>
          <div className="visual-card">
            <div className="card-header">
              <span className="dot red"></span>
              <span className="dot yellow"></span>
              <span className="dot green"></span>
            </div>
            <div className="card-body">
              <div className="line long"></div>
              <div className="line medium"></div>
              <div className="line short"></div>
              <div className="chart-mockup"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Upload Section */}
      <section id="upload" className="upload-section">
        <div className="section-header">
          <h2 className="section-title">Upload Your Document</h2>
          <p className="section-subtitle">Start the analysis by providing a subject and document</p>
        </div>
        <div className="glass-card upload-card">
          <div className="subject-input-container">
            <label htmlFor="subject-name" className="subject-label">Subject Name</label>
            <input
              id="subject-name"
              type="text"
              className="subject-field"
              placeholder="e.g. Data Structures, Operating Systems, Biology..."
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
            />
          </div>

          <div
            className={`upload-area ${file ? "has-file" : ""}`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={(e) => {
              e.preventDefault();
              setFile(e.dataTransfer.files[0]);
            }}
          >
            <div className="upload-placeholder">
              <div className="cloud-icon-wrapper">
                <FaUpload className="cloud-icon" />
              </div>
              <p className="upload-text">Choose a file or drag & drop it here</p>
              <p className="upload-subtext">PDF, DOCX formats, up to 50MB</p>

              <label htmlFor="file-upload" className="browse-btn">
                Browse File
              </label>
              <input
                id="file-upload"
                type="file"
                onChange={handleFileChange}
                accept=".pdf,.docx,.doc"
                style={{ display: "none" }}
              />
            </div>
          </div>

          {file && (
            <div className="file-list">
              <div className="file-item">
                <div className="file-icon-wrapper">
                  <FaFilePdf className="file-type-icon" />
                </div>
                <div className="file-details">
                  <div className="file-header">
                    <span className="file-name">{file.name}</span>
                    <span className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                  </div>
                  {isUploading && (
                    <div className="progress-container">
                      <div className="progress-bar" style={{ width: "100%" }}></div>
                    </div>
                  )}
                  {!isUploading && !message && (
                    <div className="file-status">Ready to upload</div>
                  )}
                </div>
                <button className="remove-btn" onClick={() => setFile(null)}>×</button>
              </div>
            </div>
          )}

          <button
            className={`upload-action-btn ${!file || isUploading ? "disabled" : ""}`}
            onClick={uploadDocument}
            disabled={!file || isUploading}
          >
            {isUploading ? "Processing..." : "Extract Insights"}
          </button>

          {message && (
            <div className={`message ${message.includes("✅") ? "success" : "error"}`}>
              {message.includes("✅") ? <FaCheckCircle /> : <FaExclamationTriangle />}
              <span>{message}</span>
              {message.includes("✅") && (
                <button onClick={() => navigate("/topics")} className="view-insights-inline-btn">
                  View Results →
                </button>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features-section">
        <h2 className="section-title">Process Overview</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="icon-wrapper purple"><FaFilePdf /></div>
            <h3>Intelligent Parsing</h3>
            <p>Our NLP engine splits your document into paragraphs and sentences for high-precision extraction.</p>
          </div>
          <div className="feature-card">
            <div className="icon-wrapper blue"><FaRobot /></div>
            <h3>Knowledge Graph</h3>
            <p>We identify key concepts (bigrams) and importance levels to build a structured knowledge base.</p>
          </div>
          <div className="feature-card">
            <div className="icon-wrapper pink"><FaRocket /></div>
            <h3>Smart Downloads</h3>
            <p>Export your tailored study notes in professional PDF format, ready for revision or sharing.</p>
          </div>
        </div>
      </section>
    </main>
  );
}

export default App;
