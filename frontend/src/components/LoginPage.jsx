import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FaEnvelope, FaLock, FaSignInAlt } from 'react-icons/fa';
import { GoogleLogin } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import './LoginPage.css';

const LoginPage = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [errorMsg, setErrorMsg] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Check cache
        const cachedEmail = localStorage.getItem('knowledgeAI_email');
        if (cachedEmail) {
            setRememberMe(true);
        }
    }, []);

    const handleGoogleSuccess = (credentialResponse) => {
        const decoded = jwtDecode(credentialResponse.credential);
        const { email, name, picture } = decoded;
        handleAuth(email, name, picture);
    };

    const handleAuth = async (userEmail, userName, userPicture, userPassword = "") => {
        try {
            const response = await fetch("http://127.0.0.1:8000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email: userEmail, name: userName, picture: userPicture, password: userPassword })
            });

            let data;
            try {
                data = await response.json();
            } catch (e) {
                const text = await response.text();
                throw new Error(`Invalid JSON response (${response.status}): ${text}`);
            }

            if (response.ok && !data.error) {
                if (rememberMe) {
                    localStorage.setItem('knowledgeAI_email', userEmail);
                } else {
                    localStorage.removeItem('knowledgeAI_email');
                }

                localStorage.setItem('knowledgeAI_token', data.token || '');
                localStorage.setItem('knowledgeAI_loggedIn', 'true');
                navigate('/');
            } else {
                setErrorMsg(data.error || `Login failed (${response.status})`);
            }
        } catch (error) {
            console.error("Login error: ", error);
            setErrorMsg(error.message || "Network error occurred");
        }
    };

    const handleSignup = async (e) => {
        e.preventDefault();
        setErrorMsg('');
        if (!email || !password || (!isLogin && !name)) {
            setErrorMsg('Please fill in all required fields');
            return;
        }

        if (isLogin) {
            await handleAuth(email, "", "", password);
        } else {
            try {
                const response = await fetch("http://127.0.0.1:8000/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email: email, name: name, password: password })
                });

                let data;
                try {
                    data = await response.json();
                } catch (e) {
                    const text = await response.text();
                    throw new Error(`Invalid JSON response (${response.status}): ${text}`);
                }

                if (response.ok && !data.error) {
                    // Successful signup, auto-login
                    await handleAuth(email, name, "", password);
                } else {
                    setErrorMsg(data.error || `Signup failed (${response.status})`);
                }
            } catch (error) {
                console.error("Signup error: ", error);
                setErrorMsg(error.message || "Network error occurred");
            }
        }
    };

    return (
        <div className="login-container">
            <div className="login-background">
                <div className="shape shape-1"></div>
                <div className="shape shape-2"></div>
                <div className="shape shape-3"></div>
            </div>
            <div className="login-card">
                <div className="login-header">
                    <div className="logo-row">
                        <img src="/assets/logo.png" alt="KnowledgeAI Logo" className="login-logo" onError={(e) => e.target.style.display = 'none'} />
                        <div className="brand">
                            <h1 className="brand-title">KnowledgeAI</h1>
                            <span className="brand-subtitle">Knowledge powered by intelligence</span>
                        </div>
                    </div>

                    <h2>{isLogin ? "Welcome back" : "Create your account"}</h2>
                    <p className="subtitle">{isLogin ? "Sign in to continue your knowledge journey" : "Sign up and start exploring"}</p>
                </div>

                <div className="login-form">
                    {errorMsg && <div className="error-message">{errorMsg}</div>}

                    <form onSubmit={handleSignup} className="form-grid">
                        {!isLogin && (
                            <div className="input-field">
                                <FaSignInAlt className="input-icon" />
                                <input
                                    type="text"
                                    placeholder="Full name"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    required={!isLogin}
                                />
                            </div>
                        )}

                        <div className="input-field">
                            <FaEnvelope className="input-icon" />
                            <input
                                type="email"
                                placeholder="Email address"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        <div className="input-field">
                            <FaLock className="input-icon" />
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <label className="remember-me">
                                <input
                                    type="checkbox"
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                />
                                <span>Remember me</span>
                            </label>
                        </div>

                        <button type="submit" className="login-btn">
                            {isLogin ? "Sign In" : "Sign Up"}
                        </button>
                    </form>

                    <div className="divider">
                        <span>OR</span>
                    </div>

                    <div className="social-login">
                        <GoogleLogin
                            onSuccess={handleGoogleSuccess}
                            onError={() => {
                                console.log('Login Failed');
                                setErrorMsg('Google login failed');
                            }}
                            useOneTap={isLogin}
                            theme="filled_black"
                            shape="pill"
                            size="large"
                            text={isLogin ? "continue_with" : "signup_with"}
                            width="260"
                        />
                    </div>

                    <div className="toggle-mode">
                        <p>
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                            <span
                                onClick={() => { setIsLogin(!isLogin); setErrorMsg(''); }}
                            >
                                {isLogin ? "Sign Up" : "Sign In"}
                            </span>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LoginPage;
