import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { FaClock, FaBrain, FaArrowLeft, FaCheck } from "react-icons/fa";
import "./QuizPage.css";

function QuizPage() {
    const { topic } = useParams();
    const navigate = useNavigate();
    const [questions, setQuestions] = useState([]);
    const [answers, setAnswers] = useState({});
    const [timeLeft, setTimeLeft] = useState(600); // 10 minutes
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchQuiz = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/generate-quiz", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ topic: decodeURIComponent(topic) })
                });
                const data = await res.json();
                if (data.error) throw new Error(data.error);
                setQuestions(data.questions);
            } catch (err) {
                setError("Failed to load assessment. Please try again.");
            } finally {
                setLoading(false);
            }
        };
        fetchQuiz();
    }, [topic]);

    useEffect(() => {
        if (timeLeft <= 0) {
            submitQuiz();
            return;
        }
        const timer = setInterval(() => setTimeLeft(t => t - 1), 1000);
        return () => clearInterval(timer);
    }, [timeLeft]);

    const handleOptionChange = (qIndex, optIndex) => {
        setAnswers({ ...answers, [qIndex]: optIndex });
    };

    const handleTextChange = (qIndex, text) => {
        setAnswers({ ...answers, [qIndex]: text });
    };

    const submitQuiz = () => {
        navigate("/result", { state: { questions, answers, topic } });
    };

    if (loading) return (
        <div className="quiz-loading">
            <div className="loader"></div>
            <h3>Generating AI Assessment...</h3>
            <p>Crafting 10 custom questions based on your document content.</p>
        </div>
    );

    if (error) return (
        <div className="quiz-error">
            <h2>Error</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
        </div>
    );

    return (
        <div className="quiz-page anim-fade-in">
            <div className="quiz-navbar">
                <button onClick={() => navigate("/topics")} className="back-btn" style={{ zIndex: 1100 }}>
                    <FaArrowLeft /> Exit
                </button>
                <div className="quiz-info">
                    <span className="quiz-topic">{decodeURIComponent(topic)}</span>
                    <div className="timer-box">
                        <FaClock />
                        <span>{Math.floor(timeLeft / 60)}:{String(timeLeft % 60).padStart(2, '0')}</span>
                    </div>
                </div>
            </div>

            <div className="questions-container">
                {questions.map((q, i) => (
                    <div key={i} className="question-card anim-slide-up" style={{ animationDelay: `${i * 0.1}s` }}>
                        <div className="question-header">
                            <span className="q-number">Question {i + 1}</span>
                            <span className={`difficulty-badge ${q.difficulty}`}>
                                {q.difficulty.toUpperCase()}
                            </span>
                        </div>
                        <p className="question-text">{q.question}</p>

                        {q.type === "mcq" ? (
                            <div className="options-grid">
                                {q.options.map((opt, idx) => (
                                    <label key={idx} className={`option-label ${answers[i] === idx ? 'selected' : ''}`}>
                                        <input
                                            type="radio"
                                            name={`q${i}`}
                                            checked={answers[i] === idx}
                                            onChange={() => handleOptionChange(i, idx)}
                                        />
                                        <span className="opt-letter">{String.fromCharCode(65 + idx)}</span>
                                        <span className="opt-text">{opt}</span>
                                    </label>
                                ))}
                            </div>
                        ) : (
                            <textarea
                                className="problem-input"
                                placeholder="Explain your approach or write code here..."
                                value={answers[i] || ""}
                                onChange={(e) => handleTextChange(i, e.target.value)}
                            />
                        )}
                    </div>
                ))}
            </div>

            <div className="quiz-footer">
                <div className="progress-info">
                    {Object.keys(answers).length} of {questions.length} Answered
                </div>
                <button className="submit-btn" onClick={submitQuiz}>
                    Submit Assessment <FaCheck />
                </button>
            </div>
        </div>
    );
}

export default QuizPage;
