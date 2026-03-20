import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaUserCircle, FaFilePdf, FaTrophy, FaCalendarAlt, FaFileAlt } from 'react-icons/fa';
import { apiUrl } from '../apiConfig';
import './Dashboard.css';

const Dashboard = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDashboardData = async () => {
            const token = localStorage.getItem('knowledgeAI_token');
            if (!token) {
                navigate('/login');
                return;
            }

            try {
                const response = await fetch(apiUrl('/user-dashboard'), {
                    headers: { 'Authorization': `Bearer ${token}` }
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch dashboard data');
                }

                const data = await response.json();
                setDashboardData(data);
            } catch (err) {
                console.error("Dashboard fetch error:", err);
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, [navigate]);

    if (loading) return <div className="dashboard-loading">Loading Dashboard... <div className="loader"></div></div>;
    if (error) return <div className="dashboard-error">Error: {error}</div>;

    const { user, documents, assessments } = dashboardData;

    return (
        <div className="dashboard-container anim-fade-in">
            <div className="dashboard-header">
                <div className="user-profile">
                    {user.picture ? (
                        <img src={user.picture} alt="Profile" className="profile-pic" />
                    ) : (
                        <FaUserCircle className="profile-icon" />
                    )}
                    <div className="user-info">
                        <h2>Welcome, {user.name || user.email.split('@')[0]}!</h2>
                        <p>{user.email}</p>
                    </div>
                </div>
            </div>

            <div className="dashboard-grid">
                {/* Documents Section */}
                <div className="dashboard-card documents-card">
                    <div className="card-header">
                        <FaFilePdf className="header-icon blue" />
                        <h3>Previously Extracted Documents</h3>
                    </div>
                    <div className="card-body">
                        {documents && documents.length > 0 ? (
                            <ul className="dashboard-list docs-list">
                                {documents.map(doc => (
                                    <li 
                                        key={doc.id} 
                                        className="list-item document-item"
                                        onClick={() => navigate('/topics', { state: { document_id: doc.id } })}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        <div className="item-details">
                                            <h4><FaFileAlt className="item-icon" /> {doc.title}</h4>
                                            <span className="subject-tag">{doc.subject}</span>
                                        </div>
                                        <div className="item-meta">
                                            <FaCalendarAlt /> {new Date(doc.uploaded_at).toLocaleDateString()}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="empty-state">No documents extracted yet. Head to Home to upload one!</p>
                        )}
                    </div>
                </div>

                {/* Assessments Section */}
                <div className="dashboard-card assessments-card">
                    <div className="card-header">
                        <FaTrophy className="header-icon gold" />
                        <h3>Recent Assessment Scores</h3>
                    </div>
                    <div className="card-body">
                        {assessments && assessments.length > 0 ? (
                            <ul className="dashboard-list scores-list">
                                {assessments.map(a => (
                                    <li key={a.id} className="list-item score-item">
                                        <div className="item-details">
                                            <h4>{decodeURIComponent(a.topic)}</h4>
                                            <div className="score-bar-container">
                                                <div className="score-bar" style={{ width: `${a.percentage}%`, backgroundColor: a.percentage >= 70 ? '#4caf50' : '#f44336' }}></div>
                                            </div>
                                        </div>
                                        <div className="item-meta score-meta">
                                            <span className={`score-badge ${a.percentage >= 70 ? 'high' : 'low'}`}>
                                                {a.percentage}% ({a.score}/{a.total})
                                            </span>
                                            <span className="date-text"><FaCalendarAlt /> {new Date(a.completed_at).toLocaleDateString()}</span>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="empty-state">No assessments completed yet. Analyze a document to start!</p>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
