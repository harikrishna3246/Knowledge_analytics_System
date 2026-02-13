import { useEffect, useState } from "react";
import { FaFileAlt, FaLightbulb, FaFileDownload, FaArrowLeft, FaClock, FaBrain } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import TopicChat from "./TopicChat";
import "./TopicInsights.css";

function TopicInsights() {
    const [topics, setTopics] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState("");
    const [filter, setFilter] = useState("ALL");
    const [openIndex, setOpenIndex] = useState(null);

    const navigate = useNavigate();

    // Helper to render content that might be strings or objects (AI response variance)
    const renderContent = (item) => {
        if (!item) return "";
        if (typeof item === 'string') return item;
        if (typeof item === 'object') {
            // Priority fields for different structured AI responses
            const textValue = item.description || item.point || item.importance || item.explanation || item.text || item.content;
            if (textValue) return textValue;
            // Fallback: join all string values
            return Object.values(item).filter(v => typeof v === 'string').join(": ");
        }
        return String(item);
    };


    useEffect(() => {
        setLoading(true);
        fetch("http://127.0.0.1:8000/get-stored-topics")
            .then(res => {
                if (!res.ok) throw new Error("Failed to fetch topics");
                return res.json();
            })
            .then(data => {
                // Robust verification: ensure data is an array
                if (Array.isArray(data)) {
                    setTopics(data);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    setTopics([]);
                }
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    const triggerManualAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch("http://127.0.0.1:8000/store-topics-with-content", {
                method: "POST",
            });
            if (!res.ok) throw new Error("Analysis failed");
            // Refresh topics
            const refreshRes = await fetch("http://127.0.0.1:8000/get-stored-topics");
            const data = await refreshRes.json();
            setTopics(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return (
        <div className="insights-page">
            <div className="loading-state">
                <FaClock className="spin-icon" style={{ fontSize: "3rem", marginBottom: "1rem", color: "var(--accent)" }} />
                <h2>Harvesting Knowledge...</h2>
                <p>Curating the most relevant concepts from your documents.</p>
            </div>
        </div>
    );

    if (error) return (
        <div className="insights-page">
            <div className="error-state">
                <h2>Ops! Something went wrong</h2>
                <p>{error}</p>
                <button onClick={() => window.location.reload()} className="retry-btn">Retry Connection</button>
            </div>
        </div>
    );

    const priorityOrder = { "HIGH": 1, "MEDIUM": 2, "LOW": 3 };

    const filteredTopics = topics
        .filter(t => t.topic?.toLowerCase().includes(search.toLowerCase()))
        .filter(t => filter === "ALL" || (t.priority || t.importance) === filter)
        .sort((a, b) => {
            const pA = (a.priority || a.importance || "LOW").toUpperCase();
            const pB = (b.priority || b.importance || "LOW").toUpperCase();
            return (priorityOrder[pA] || 4) - (priorityOrder[pB] || 4);
        });

    return (
        <div className="insights-page">
            <div className="page-header">
                <button onClick={() => navigate("/")} className="back-nav">
                    <FaArrowLeft /> Exit to Dashboard
                </button>
                <h1 className="page-title">Knowledge Insights</h1>
                <p className="page-subtitle">Interactive deep-dive into your document's intelligence nodes.</p>
            </div>

            {topics.length === 0 ? (
                <div className="no-topics">
                    <div className="no-topics-icon"><FaBrain /></div>
                    <h2>No Intelligence Nodes Found</h2>
                    <p>It seems this document is either empty or too short for automatic concept mapping.
                        Try running a special deep-dive analysis manually.</p>
                    <button className="manual-analyze-btn" onClick={triggerManualAnalysis}>
                        Deep-Dive Analysis
                    </button>
                </div>
            ) : (
                <div className="insights-container">
                    <div className="controls">
                        <input
                            className="search-box"
                            placeholder="Search topic..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                        />

                        <select
                            className="filter-box"
                            value={filter}
                            onChange={(e) => setFilter(e.target.value)}
                        >
                            <option value="ALL">All Priorities</option>
                            <option value="HIGH">High Priority</option>
                            <option value="MEDIUM">Medium Priority</option>
                            <option value="LOW">Low Priority</option>
                        </select>
                    </div>

                    <div className="topic-selection-grid">
                        {filteredTopics.map((t, index) => (
                            <div
                                className={`selection-card ${(t.priority || t.importance || "").toLowerCase()} ${openIndex === index ? 'expanded' : ''}`}
                                key={index}
                            >
                                <div className="card-header-main" onClick={() => {
                                    setOpenIndex(openIndex === index ? null : index);
                                }}>
                                    <div className="card-badge">{(t.priority || t.importance)} priority</div>
                                    <h3>{t.topic}</h3>
                                    <button className="toggle-btn">
                                        {openIndex === index ? "Hide Logic" : "Read Insights"}
                                    </button>
                                </div>

                                {openIndex === index && (
                                    <div className="expanded-knowledge anim-fade-in">
                                        <div className="content-grid">
                                            <div className="content-box">
                                                <h4><FaFileAlt /> From Document</h4>
                                                <ul>
                                                    {Array.isArray(t.from_document) ? (
                                                        t.from_document.map((p, i) => (
                                                            <li key={i}>{renderContent(p)}</li>
                                                        ))
                                                    ) : t.from_document ? (
                                                        <li>{renderContent(t.from_document)}</li>
                                                    ) : (
                                                        <li>No content available.</li>
                                                    )}
                                                </ul>
                                            </div>

                                            <div className="content-box">
                                                <h4><FaLightbulb /> Academic Insights</h4>
                                                <ul>
                                                    {Array.isArray(t.academic_knowledge || t.from_external) ? (
                                                        (t.academic_knowledge || t.from_external || []).map((p, i) => (
                                                            <li key={i}>{renderContent(p)}</li>
                                                        ))
                                                    ) : (t.academic_knowledge || t.from_external) ? (
                                                        <li>{renderContent(t.academic_knowledge || t.from_external)}</li>
                                                    ) : (
                                                        <li>No insights available.</li>
                                                    )}
                                                </ul>
                                            </div>

                                            {(t.real_world_example || t.real_world_example === "") && (
                                                <div className="content-box">
                                                    <h4><FaBrain /> Real-world Application</h4>
                                                    <p style={{ fontSize: "0.9rem", lineHeight: "1.6", color: "#5a4b44", margin: 0 }}>
                                                        {renderContent(t.real_world_example) || "N/A"}
                                                    </p>
                                                </div>
                                            )}
                                        </div>

                                        <TopicChat
                                            topic={t.topic}
                                            documentContext={Array.isArray(t.from_document) ? t.from_document.map(renderContent).join("\n") : renderContent(t.from_document)}
                                        />

                                        <div className="card-actions-row">
                                            <a
                                                className="download-pdf-btn"
                                                href={`http://127.0.0.1:8000/download-topic-pdf/${encodeURIComponent(t.topic)}`}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                            >
                                                <FaFileDownload /> Export Study Notes (PDF)
                                            </a>
                                            <button
                                                className="take-quiz-btn"
                                                onClick={() => navigate(`/quiz/${encodeURIComponent(t.topic)}`)}
                                            >
                                                Take Assessment
                                            </button>
                                        </div>

                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                    {filteredTopics.length === 0 && search && (
                        <div className="no-results">
                            <p>No topics found matching "{search}"</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default TopicInsights;
