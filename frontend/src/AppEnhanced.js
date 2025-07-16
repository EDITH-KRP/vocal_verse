import React, { useState, useEffect, useRef } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AuthPage from './components/Auth/AuthPage';
import Dashboard from './components/Analytics/Dashboard';
import axios from 'axios';
import './App.css';

const VoiceInventoryApp = () => {
  const [products, setProducts] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [activeTab, setActiveTab] = useState('inventory');
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);
  const { user, logout } = useAuth();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  const languageConfig = {
    'en': { name: 'English', code: 'en-US' },
    'hi': { name: 'हिंदी', code: 'hi-IN' },
    'kn': { name: 'ಕನ್ನಡ', code: 'kn-IN' },
    'ta': { name: 'தமிழ்', code: 'ta-IN' },
    'te': { name: 'తెలుగు', code: 'te-IN' }
  };

  useEffect(() => {
    initializeSpeechRecognition();
    initializeSpeechSynthesis();
    loadProducts();
  }, []);

  useEffect(() => {
    if (recognitionRef.current) {
      recognitionRef.current.lang = languageConfig[language].code;
    }
  }, [language]);

  const initializeSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setVoiceSupported(true);
    } else {
      setVoiceSupported(false);
      setError('Voice recognition not supported in this browser');
    }
  };

  const initializeSpeechSynthesis = () => {
    if ('speechSynthesis' in window) {
      synthRef.current = window.speechSynthesis;
    }
  };

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${BACKEND_URL}/products`);
      setProducts(response.data.products || []);
    } catch (err) {
      console.error('Failed to load products:', err);
      setError('Failed to load products: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const processVoiceCommand = async (command) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${BACKEND_URL}/voice-command`, {
        command: command,
        language: language
      });
      
      if (response.data.success) {
        setResponse(JSON.stringify(response.data, null, 2));
        loadProducts(); // Refresh products list
        speakResponse(response.data);
      } else {
        setError(response.data.message || 'Command processing failed');
      }
    } catch (err) {
      console.error('Voice command error:', err);
      setError('Failed to process command: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const speakResponse = (data) => {
    if (!synthRef.current) return;
    
    let textToSpeak = '';
    
    if (data.message) {
      textToSpeak = data.message;
    } else if (data.success) {
      textToSpeak = 'Command executed successfully';
    }
    
    if (textToSpeak) {
      synthRef.current.cancel();
      const utterance = new SpeechSynthesisUtterance(textToSpeak);
      utterance.lang = languageConfig[language].code;
      utterance.rate = 0.8;
      utterance.pitch = 1;
      synthRef.current.speak(utterance);
    }
  };

  const startListening = () => {
    if (!voiceSupported) {
      setError('Voice recognition not supported in this browser');
      return;
    }

    if (isListening) return;

    setTranscript('');
    setError('');
    setResponse('');
    
    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = languageConfig[language].code;
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError('');
      };
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setTranscript(transcript);
        processVoiceCommand(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current.onerror = (event) => {
        setError('Voice recognition error: ' + event.error);
        setIsListening(false);
      };

      recognitionRef.current.start();
    } catch (err) {
      setError('Failed to start voice recognition: ' + err.message);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
        recognitionRef.current = null;
      } catch (err) {
        console.error('Error stopping recognition:', err);
      }
    }
    setIsListening(false);
  };

  const formatPrice = (price) => {
    return `₹${price}`;
  };

  const ProductCard = ({ product }) => (
    <div className="product-card">
      <div className="product-header">
        <h3>{product.name}</h3>
        <div className="product-meta">
          <span className="quantity">{product.quantity} kg</span>
          <span className="price">{formatPrice(product.price_per_kg)}/kg</span>
        </div>
      </div>
      
      {product.description && (
        <p className="product-description">{product.description}</p>
      )}
      
      <div className="product-details">
        <div className="product-category">
          Category: {product.category}
        </div>
        {product.minimum_stock && (
          <div className="minimum-stock">
            Min Stock: {product.minimum_stock} kg
          </div>
        )}
        {product.supplier && (
          <div className="supplier">
            Supplier: {product.supplier}
          </div>
        )}
      </div>
      
      {product.quantity <= (product.minimum_stock || 1) && (
        <div className="low-stock-warning">
          ⚠️ Low Stock Alert
        </div>
      )}
    </div>
  );

  return (
    <div className="App">
      {/* Navigation Header */}
      <header className="App-header">
        <div className="header-content">
          <div className="header-left">
            <h1>🎤 Vocal Verse</h1>
            <p>Voice-Powered Inventory Management</p>
          </div>
          <div className="header-right">
            <span className="user-info">Welcome, {user?.full_name || user?.email}</span>
            <button onClick={logout} className="logout-button">
              Logout
            </button>
          </div>
        </div>
        
        {/* Tab Navigation */}
        <nav className="tab-navigation">
          <button 
            className={`tab-button ${activeTab === 'inventory' ? 'active' : ''}`}
            onClick={() => setActiveTab('inventory')}
          >
            📦 Inventory
          </button>
          <button 
            className={`tab-button ${activeTab === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveTab('analytics')}
          >
            📊 Analytics
          </button>
        </nav>
      </header>

      {activeTab === 'inventory' && (
        <div className="inventory-section">
          {/* Language Selection */}
          <div className="language-selector">
            <label>Language: </label>
            <select value={language} onChange={(e) => setLanguage(e.target.value)}>
              {Object.entries(languageConfig).map(([code, config]) => (
                <option key={code} value={code}>{config.name}</option>
              ))}
            </select>
          </div>

          {/* Voice Controls */}
          <div className="voice-controls">
            <button 
              className={`voice-button ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              disabled={!voiceSupported}
            >
              {isListening ? '🔴 Stop' : '🎤 Start Voice'}
            </button>
            
            {!voiceSupported && (
              <p className="error">Voice recognition not supported in this browser</p>
            )}
          </div>

          {/* Status Display */}
          {loading && <div className="loading">Processing...</div>}
          {error && <div className="error">{error}</div>}
          {transcript && (
            <div className="transcript">
              <strong>You said:</strong> {transcript}
            </div>
          )}
          {response && (
            <div className="response">
              <strong>Response:</strong>
              <pre>{response}</pre>
            </div>
          )}

          {/* Products List */}
          <div className="products-section">
            <h2>Products ({products.length})</h2>
            <div className="products-grid">
              {products.map((product, index) => (
                <ProductCard key={product.id || index} product={product} />
              ))}
            </div>
            
            {products.length === 0 && !loading && (
              <div className="empty-state">
                <p>No products found. Try saying "Add tomato 5 kg at 20 rupees"</p>
              </div>
            )}
          </div>

          {/* Enhanced Help Section */}
          <div className="help-section">
            <h3>Voice Commands Examples:</h3>
            <div className="help-categories">
              <div className="help-category">
                <h4>📦 Inventory Management</h4>
                <ul>
                  <li>"Add tomato 5 kg at 20 rupees"</li>
                  <li>"Update tomato price to 25 rupees"</li>
                  <li>"Remove tomato"</li>
                  <li>"List all products"</li>
                  <li>"Search for tomato"</li>
                </ul>
              </div>
              <div className="help-category">
                <h4>📊 Analytics & Predictions</h4>
                <ul>
                  <li>"Predict tomato stock for 7 days"</li>
                  <li>"Analyze tomato consumption"</li>
                  <li>"Show low stock alerts"</li>
                  <li>"Generate inventory report"</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'analytics' && (
        <Dashboard />
      )}
    </div>
  );
};

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner"></div>
        <p>Loading...</p>
      </div>
    );
  }
  
  return isAuthenticated ? children : <Navigate to="/auth" />;
};

const AppEnhanced = () => {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
            }}
          />
          <Routes>
            <Route path="/auth" element={<AuthPage />} />
            <Route 
              path="/" 
              element={
                <ProtectedRoute>
                  <VoiceInventoryApp />
                </ProtectedRoute>
              } 
            />
            <Route path="*" element={<Navigate to="/" />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
};

export default AppEnhanced;