import { useEffect, useState } from "react";
import { FaFileAlt, FaLightbulb, FaFileDownload, FaArrowLeft, FaClock, FaBrain, FaRocket } from "react-icons/fa";
import { useNavigate, useLocation } from "react-router-dom";
import TopicChat from "./TopicChat";
import "./TopicInsights.css";
import { apiUrl } from '../apiConfig';

function TopicInsights() {
    const [topics, setTopics] = useState([]);
    const [subject, setSubject] = useState("");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState("");
    const [filter, setFilter] = useState("ALL");

    const navigate = useNavigate();
    const location = useLocation();
    const document_id = location.state?.document_id || null;

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const token = sessionStorage.getItem('knowledgeAI_token');
                const queryParam = document_id ? `?document_id=${document_id}` : "";

                // 1. Get topics
                const res = await fetch(apiUrl(`/get-stored-topics${queryParam}`), {
                    headers: { Authorization: `Bearer ${token}` }
                });
                if (!res.ok) throw new Error("Failed to fetch topics");
                const data = await res.json();

                if (Array.isArray(data)) {
                    setTopics(data);
                } else if (data.error) {
                    throw new Error(data.error);
                } else {
                    setTopics([]);
                }

                // 2. Get the latest document to show subject
                const docsRes = await fetch(apiUrl("/get-documents"), {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const docsData = await docsRes.json();
                if (docsData.documents && docsData.documents.length > 0) {
                    if (document_id) {
                        const targetDoc = docsData.documents.find(d => d.id === document_id);
                        if (targetDoc) {
                            setSubject(targetDoc.subject || targetDoc.title);
                        } else {
                            setSubject(docsData.documents[0].subject);
                        }
                    } else {
                        setSubject(docsData.documents[0].subject);
                    }
                }
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const triggerManualAnalysis = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = sessionStorage.getItem('knowledgeAI_token');
            const queryParam = document_id ? `?document_id=${document_id}` : "";

            const res = await fetch(apiUrl(`/store-topics-with-content${queryParam}`), {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error("Analysis failed");

            const refreshRes = await fetch(apiUrl(`/get-stored-topics${queryParam}`), {
                headers: { Authorization: `Bearer ${token}` }
            });
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
                <FaClock className="spin-icon" style={{ fontSize: "3rem", marginBottom: "1rem", color: "#8e6cef" }} />
                <h2>Harvesting Knowledge...</h2>
                <p>Building your intelligence map.</p>
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
            <button onClick={() => navigate("/home")} className="back-nav" style={{ zIndex: 1100 }}>
                <FaArrowLeft /> Back
            </button>
            <h1 className="page-title">{subject ? `${subject} Insights` : "Knowledge Insights"}</h1>
            <p className="page-subtitle">Structured understanding extracted from your document.</p>

            <div className="controls">
                <input
                    className="search-box"
                    placeholder="Search topics..."
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

            {topics.length === 0 ? (
                <div className="no-topics">
                    <div className="no-topics-icon"><FaBrain /></div>
                    <h2>No Insights Extracted</h2>
                    <p>Click below to run a deep-dive analysis on your document.</p>
                    <button className="manual-analyze-btn" onClick={triggerManualAnalysis}>
                        Deep-Dive Analysis <FaRocket />
                    </button>
                </div>
            ) : (
                <div className="topic-list">
                    {filteredTopics.map((topic, index) => (
                        <TopicCard key={index} topicData={topic} />
                    ))}
                    {filteredTopics.length === 0 && search && (
                        <p style={{ textAlign: 'center', color: '#666' }}>No results for "{search}"</p>
                    )}
                </div>
            )}
        </div>
    );
}

function TopicCard({ topicData }) {
    const [open, setOpen] = useState(false);
    const priority = (topicData.priority || topicData.importance || "LOW").toUpperCase();

    return (
        <div className={`topic-card ${open ? 'expanded' : ''}`}>
            <div className="topic-header" onClick={() => setOpen(!open)}>
                <span className={`priority ${priority.toLowerCase()}`}>
                    {priority}
                </span>
                <h3>{topicData.topic}</h3>
                <button className="toggle-btn">
                    {open ? "Hide" : "Read Insights"}
                </button>
            </div>

            {open && <TopicDetails topic={topicData} />}
        </div>
    );
}

function TopicDetails({ topic }) {
    const navigate = useNavigate();
    const [showChat, setShowChat] = useState(false);

    const renderArrayContent = (content) => {
        if (!content) return <li>No specific data extracted.</li>;
        const items = Array.isArray(content) ? content : [content];

        return items.map((item, i) => {
            let text = "";
            if (typeof item === 'string') text = item;
            else if (typeof item === 'object') {
                text = item.description || item.point || item.explanation || JSON.stringify(item);
            }
            return <li key={i}>{text}</li>;
        });
    };

    return (
        <div className="topic-details anim-fade-in">
            <div className="details-grid">
                <div className="detail-box">
                    <h4><FaFileAlt /> From Document</h4>
                    <ul>
                        {renderArrayContent(topic.from_document)}
                    </ul>
                </div>

                <div className="detail-box">
                    <h4><FaLightbulb /> AI Insights</h4>
                    <ul>
                        {renderArrayContent(topic.academic_knowledge || topic.from_external)}
                    </ul>
                </div>

                {topic.real_world_example && (
                    <div className="detail-box" style={{ gridColumn: 'span 2' }}>
                        <h4><FaBrain /> Real-world Application</h4>
                        <p style={{ fontSize: '0.95rem', color: '#444', margin: 0 }}>{topic.real_world_example}</p>
                    </div>
                )}
            </div>

            {showChat && (
                <div className="chat-popup-container anim-slide-up">
                    <TopicChat
                        topic={topic.topic}
                        documentContext={Array.isArray(topic.from_document) ? topic.from_document.join("\n") : topic.from_document}
                    />
                </div>
            )}

            <div className="actions">
                <button
                    className={`btn secondary ${showChat ? 'active' : ''}`}
                    onClick={() => setShowChat(!showChat)}
                >
                    {showChat ? "Close AI Assistant" : "Ask AI Assistant"}
                </button>
                <button
                    className="btn"
                    onClick={() => navigate(`/quiz/${encodeURIComponent(topic.topic)}`)}
                >
                    Take Assessment
                </button>
                <button
                    className="btn outline"
                    onClick={async () => {
                        const token = sessionStorage.getItem('knowledgeAI_token');
                        try {
                            const res = await fetch(
                                apiUrl(`/download-topic-pdf/${encodeURIComponent(topic.topic)}`),
                                { headers: { Authorization: `Bearer ${token}` } }
                            );
                            if (!res.ok) throw new Error('Failed to download PDF');
                            const blob = await res.blob();
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `${topic.topic}.pdf`;
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                            URL.revokeObjectURL(url);
                        } catch (err) {
                            console.error(err);
                            alert('Failed to download PDF.');
                        }
                    }}
                >
                    <FaFileDownload /> Export PDF
                </button>
            </div>
        </div>
    );
}

export default TopicInsights;
