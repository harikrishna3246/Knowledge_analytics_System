import { useState, useEffect, useRef } from "react";
import "./TopicChat.css";
import { FaRobot, FaUser, FaPaperPlane } from "react-icons/fa";

function TopicChat({ topic, documentContext }) {
    const [question, setQuestion] = useState("");
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, loading]);

    const askAI = async () => {
        if (!question.trim() || loading) return;

        const currentQuestion = question;
        const userMessage = { role: "user", text: currentQuestion };
        setMessages(prev => [...prev, userMessage]);
        setQuestion("");
        setLoading(true);

        try {
            const token = sessionStorage.getItem('knowledgeAI_token');
            const res = await fetch("http://127.0.0.1:8000/chat", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    topic: topic,
                    question: currentQuestion,
                    document_context: Array.isArray(documentContext) ? documentContext.join("\n") : documentContext
                })
            });

            if (!res.ok) throw new Error("Server error");

            const data = await res.json();
            setMessages(prev => [...prev, { role: "assistant", text: data.answer }]);
        } catch (error) {
            setMessages(prev => [...prev, { role: "assistant", text: "Error: Failed to connect to AI server. Please try again." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="topic-chat-container anim-fade-in">
            <div className="chat-header">
                <FaRobot className="bot-icon" />
                <span>Tutor Bot: <strong>{topic}</strong></span>
            </div>

            <div className="chat-messages" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="empty-chat">
                        <FaRobot style={{ fontSize: "2rem", marginBottom: "10px", opacity: 0.3 }} />
                        <p>Select a topic and ask me anything! <br /> I'll use the document context to help you.</p>
                    </div>
                )}
                {messages.map((m, i) => (
                    <div key={i} className={`chat-bubble ${m.role} anim-slide-up`}>
                        <div className="bubble-icon">
                            {m.role === "user" ? <FaUser /> : <FaRobot />}
                        </div>
                        <div className="bubble-text">
                            {m.text}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div className="chat-bubble assistant load-bubble">
                        <div className="bubble-icon"><FaRobot className="spin-icon" /></div>
                        <div className="bubble-text typing">AI is thinking...</div>
                    </div>
                )}
            </div>

            <div className="chat-input-area">
                <input
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    placeholder="Ask a specific question..."
                    onKeyPress={(e) => e.key === 'Enter' && askAI()}
                />
                <button onClick={askAI} disabled={loading || !question.trim()}>
                    <FaPaperPlane />
                </button>
            </div>
        </div>
    );
}

export default TopicChat;
