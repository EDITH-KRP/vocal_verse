import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const RegisterForm = ({ onToggleMode }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    
    // Clear error when user starts typing
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: ''
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.fullName) {
      newErrors.fullName = 'Full name is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setLoading(true);
    
    const result = await register(formData.email, formData.password, formData.fullName);
    
    if (result.success) {
      // Navigate to dashboard on successful registration
      navigate('/', { replace: true });
    } else {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form">
      <h2>Create Your Account</h2>
      <form onSubmit={handleSubmit} className={loading ? 'form-loading' : ''}>
        <div className="form-group">
          <label htmlFor="fullName">Full Name</label>
          <div className="input-wrapper">
            <input
              type="text"
              id="fullName"
              name="fullName"
              value={formData.fullName}
              onChange={handleChange}
              required
              placeholder="Enter your full name"
            />
            <div className="input-focus-border"></div>
          </div>
          {errors.fullName && <span className="error-text">{errors.fullName}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <div className="input-wrapper">
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="Enter your email"
            />
            <div className="input-focus-border"></div>
          </div>
          {errors.email && <span className="error-text">{errors.email}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <div className="input-wrapper">
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="Enter your password"
            />
            <div className="input-focus-border"></div>
          </div>
          {errors.password && <span className="error-text">{errors.password}</span>}
        </div>
        
        <div className="form-group">
          <label htmlFor="confirmPassword">Confirm Password</label>
          <div className="input-wrapper">
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              placeholder="Confirm your password"
            />
            <div className="input-focus-border"></div>
          </div>
          {errors.confirmPassword && <span className="error-text">{errors.confirmPassword}</span>}
        </div>
        
        <button type="submit" disabled={loading} className={`auth-button ${loading ? 'loading' : ''}`}>
          {loading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
      
      <p className="auth-toggle">
        Already have an account?{' '}
        <button type="button" onClick={onToggleMode} className="link-button">
          Login here
        </button>
      </p>
    </div>
  );
};

export default RegisterForm;