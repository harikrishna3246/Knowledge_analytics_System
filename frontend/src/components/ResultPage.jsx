import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FaTrophy, FaRedo, FaHome, FaCheckCircle, FaTimesCircle, FaExclamationCircle } from "react-icons/fa";
import { apiUrl } from "../apiConfig";
import "./ResultPage.css";

function ResultPage() {
    const { state } = useLocation();
    const navigate = useNavigate();

    const hasSaved = useRef(false);

    const questions = state?.questions || [];
    const answers = state?.answers || [];
    const topic = state?.topic || "";

    let score = 0;
    let totalMCQ = 0;

    questions.forEach((q, i) => {
        if (q.type === "mcq") {
            totalMCQ++;
            if (answers[i] === q.correct_answer) {
                score++;
            }
        }
    });

    const percentage = totalMCQ > 0 ? Math.round((score / totalMCQ) * 100) : 0;

    useEffect(() => {
        const saveScore = async () => {
            if (hasSaved.current || totalMCQ === 0 || !topic) return;
            hasSaved.current = true;
            const token = localStorage.getItem('knowledgeAI_token');
            if (token) {
                try {
                    await fetch(apiUrl('/save-assessment'), {
                        method: "POST",
                        headers: { 
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${token}`
                        },
                        body: JSON.stringify({
                            topic: topic,
                            score: score,
                            total: totalMCQ,
                            percentage: percentage
                        })
                    });
                    hasSaved.current = true;
                } catch (e) {
                    console.error("Failed to save score", e);
                }
            }
        };
        saveScore();
    }, [topic, score, totalMCQ, percentage]);

    if (!state) return <div>No evidence found.</div>;

    return (
        <div className="result-page anim-fade-in">
            <div className="result-card">
                <div className="trophy-section">
                    <FaTrophy className={`trophy-icon ${percentage >= 70 ? 'gold' : 'silver'}`} />
                    <h1>Assessment Completed</h1>
                    <p className="topic-name">{decodeURIComponent(topic)}</p>
                </div>

                <div className="score-main">
                    <div className="score-circle">
                        <span className="percent">{percentage}%</span>
                        <span className="label">Composite Score</span>
                    </div>
                    <div className="score-details">
                        <p><strong>Correct MCQs:</strong> {score} / {totalMCQ}</p>
                        <p><strong>Problem Solutions:</strong> Submitted for Review</p>
                    </div>
                </div>

                <div className="review-section">
                    <h3>Review Answers</h3>
                    {questions.map((q, i) => (
                        <div key={i} className={`review-item ${q.type}`}>
                            <div className="review-header">
                                <span className="q-num">Q{i + 1}</span>
                                {q.type === "mcq" ? (
                                    answers[i] === q.correct_answer ?
                                        <FaCheckCircle className="icon-correct" /> :
                                        <FaTimesCircle className="icon-wrong" />
                                ) : (
                                    <FaExclamationCircle className="icon-review" />
                                )}
                            </div>
                            <p className="q-text">{q.question}</p>

                            {q.type === "mcq" && (
                                <div className="ans-compare">
                                    <p className="your-ans">Your Answer: {q.options[answers[i]] || "None"}</p>
                                    <p className="correct-ans">Correct: {q.options[q.correct_answer]}</p>
                                </div>
                            )}

                            {q.type === "problem" && (
                                <div className="prob-review">
                                    <p className="your-sol"><strong>Your Solution:</strong> {answers[i] || "Empty"}</p>
                                    <div className="hint-box">
                                        <strong>Suggested Approach:</strong>
                                        <p>{q.sample_answer}</p>
                                    </div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>

                <div className="result-actions">
                    {percentage < 70 && (
                        <button onClick={() => navigate(`/quiz/${topic}`)} className="btn-retry">
                            <FaRedo /> Take Re-assessment
                        </button>
                    )}
                    <button onClick={() => navigate("/")} className="btn-home">
                        <FaHome /> Back to Home
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ResultPage;
