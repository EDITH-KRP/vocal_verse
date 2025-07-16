import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';
import './AuthPage.css';

const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const navigate = useNavigate();
  const { user, loading } = useAuth();

  // Redirect to dashboard if user is already authenticated
  useEffect(() => {
    if (!loading && user) {
      navigate('/', { replace: true });
    }
  }, [user, loading, navigate]);

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="auth-page">
        <div className="auth-container">
          <div className="loading">Checking authentication...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <h1>🎤 Vocal Verse</h1>
          <p>Voice-Powered Inventory Management</p>
        </div>
        
        {isLogin ? (
          <LoginForm onToggleMode={toggleMode} />
        ) : (
          <RegisterForm onToggleMode={toggleMode} />
        )}
      </div>
    </div>
  );
};

export default AuthPage;