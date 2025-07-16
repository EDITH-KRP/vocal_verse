import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from './contexts/AuthContext';

const VoiceDebugger = () => {
  const [testCommand, setTestCommand] = useState('add apple 2 kg at 50 rupees');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { user } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';
  const token = localStorage.getItem('token');

  const testVoiceCommand = async () => {
    setLoading(true);
    setError('');
    setResult('');

    console.log('Testing voice command:', testCommand);
    console.log('Backend URL:', BACKEND_URL);

    try {
      const response = await axios.post(`${BACKEND_URL}/voice-command`, {
        command: testCommand,
        language: 'en'
      });

      console.log('Response received:', response);
      setResult(JSON.stringify(response.data, null, 2));
    } catch (err) {
      console.error('Error details:', err);
      const errorMessage = err.response?.data?.detail || err.message;
      setError('Error: ' + errorMessage);
      
      // Log more details for debugging
      console.log('Error response:', err.response);
      console.log('Error status:', err.response?.status);
      console.log('Error data:', err.response?.data);
    } finally {
      setLoading(false);
    }
  };

  const testBackendHealth = async () => {
    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await axios.get(`${BACKEND_URL}/health`);
      console.log('Health check response:', response);
      setResult(`Health check successful: ${JSON.stringify(response.data, null, 2)}`);
    } catch (err) {
      console.error('Health check error:', err);
      setError('Backend health check failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const testAuth = async () => {
    setLoading(true);
    setError('');
    setResult('');

    try {
      const response = await axios.get(`${BACKEND_URL}/auth/me`);
      console.log('Auth check response:', response);
      setResult(`Auth check successful: ${JSON.stringify(response.data, null, 2)}`);
    } catch (err) {
      console.error('Auth check error:', err);
      setError('Auth check failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: '10px', 
      right: '10px', 
      background: 'white', 
      border: '1px solid #ccc', 
      padding: '20px', 
      borderRadius: '8px',
      boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
      zIndex: 1000,
      maxWidth: '400px'
    }}>
      <h3>Voice Command Debugger</h3>
      
      <div style={{ marginBottom: '10px' }}>
        <label>Backend URL: </label>
        <code>{BACKEND_URL}</code>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <label>User: </label>
        <code>{user ? user.email : 'Not logged in'}</code>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <label>Token: </label>
        <code>{token ? `${token.substring(0, 20)}...` : 'No token'}</code>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <label>Auth Header: </label>
        <code>{axios.defaults.headers.common['Authorization'] || 'None'}</code>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <button onClick={testBackendHealth} disabled={loading}>
          Test Backend Health
        </button>
        <button onClick={testAuth} disabled={loading} style={{ marginLeft: '10px' }}>
          Test Auth
        </button>
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <input
          type="text"
          value={testCommand}
          onChange={(e) => setTestCommand(e.target.value)}
          placeholder="Enter test command"
          style={{ width: '100%', padding: '5px' }}
        />
      </div>
      
      <div style={{ marginBottom: '10px' }}>
        <button onClick={testVoiceCommand} disabled={loading}>
          {loading ? 'Testing...' : 'Test Voice Command'}
        </button>
      </div>
      
      {error && (
        <div style={{ 
          color: 'red', 
          background: '#ffebee', 
          padding: '10px', 
          borderRadius: '4px',
          marginBottom: '10px'
        }}>
          {error}
        </div>
      )}
      
      {result && (
        <div style={{ 
          background: '#f5f5f5', 
          padding: '10px', 
          borderRadius: '4px',
          fontSize: '12px',
          maxHeight: '200px',
          overflow: 'auto'
        }}>
          <pre>{result}</pre>
        </div>
      )}
    </div>
  );
};

export default VoiceDebugger;