how import React, { useState, useEffect, useRef } from 'react';
import './App.css';

const App = () => {
  const [products, setProducts] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [lowStockAlerts, setLowStockAlerts] = useState([]);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [executingSuggestion, setExecutingSuggestion] = useState(null);
  const [aiSuggestions, setAiSuggestions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [executingSuggestion, setExecutingSuggestion] = useState(null);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

  const languageConfig = {
    'en': { name: 'English', code: 'en-IN' },
    'hi': { name: 'हिंदी', code: 'hi-IN' },
    'kn': { name: 'ಕನ್ನಡ', code: 'kn-IN' },
    'ta': { name: 'தமிழ்', code: 'ta-IN' },
    'te': { name: 'తెలుగు', code: 'te-IN' }
  };

  useEffect(() => {
    initializeSpeechRecognition();
    initializeSpeechSynthesis();
    loadProducts();
    loadAISuggestions();
    loadAnalytics();
    
    // Auto-refresh suggestions every 30 seconds
    const interval = setInterval(() => {
      loadAISuggestions();
    }, 30000);
    
    return () => clearInterval(interval);
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
      console.log('Loading products from:', `${BACKEND_URL}/api/products`);
      const loadAISuggestions = async () => {
    try {
      console.log('Loading AI suggestions from:', `${BACKEND_URL}/api/suggestions`);
      const response = await fetch(`${BACKEND_URL}/api/suggestions`);
      const data = await response.json();
      console.log('AI suggestions data:', data);
      setAiSuggestions(data.suggestions || []);
    } catch (err) {
      console.error('Failed to load AI suggestions:', err);
    }
  };

  const loadAnalytics = async () => {
    try {
      console.log('Loading analytics from:', `${BACKEND_URL}/api/analytics/dashboard`);
      const response = await fetch(`${BACKEND_URL}/api/analytics/dashboard`);
      const data = await response.json();
      console.log('Analytics data:', data);
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const executeSuggestion = async (suggestionId) => {
    try {
      setExecutingSuggestion(suggestionId);
      console.log('Executing suggestion:', suggestionId);
      const response = await fetch(`${BACKEND_URL}/api/suggestions/${suggestionId}/execute`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        setResponse(JSON.stringify(data, null, 2));
        loadProducts(); // Refresh products
        loadAISuggestions(); // Refresh suggestions
        loadAnalytics(); // Refresh analytics
        speakResponse({message: "Suggestion executed successfully"});
      } else {
        setError(data.detail || 'Failed to execute suggestion');
      }
    } catch (err) {
      console.error('Failed to execute suggestion:', err);
      setError('Failed to execute suggestion: ' + err.message);
    } finally {
      setExecutingSuggestion(null);
    }
  };

  const response = await fetch(`${BACKEND_URL}/api/products`);
      console.log('Products response status:', response.status);
      const data = await response.json();
      console.log('Products data:', data);
      setProducts(data.products || []);
      setLowStockAlerts(data.low_stock_alerts || []);
    } catch (err) {
      console.error('Failed to load products:', err);
      setError('Failed to load products: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadAISuggestions = async () => {
    try {
      console.log('Loading AI suggestions from:', `${BACKEND_URL}/api/suggestions`);
      const response = await fetch(`${BACKEND_URL}/api/suggestions`);
      const data = await response.json();
      console.log('AI suggestions data:', data);
      setAiSuggestions(data.suggestions || []);
    } catch (err) {
      console.error('Failed to load AI suggestions:', err);
    }
  };

  const loadAnalytics = async () => {
    try {
      console.log('Loading analytics from:', `${BACKEND_URL}/api/analytics/dashboard`);
      const response = await fetch(`${BACKEND_URL}/api/analytics/dashboard`);
      const data = await response.json();
      console.log('Analytics data:', data);
      setAnalytics(data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    }
  };

  const executeSuggestion = async (suggestionId) => {
    try {
      setExecutingSuggestion(suggestionId);
      console.log('Executing suggestion:', suggestionId);
      const response = await fetch(`${BACKEND_URL}/api/suggestions/${suggestionId}/execute`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (response.ok) {
        setResponse(JSON.stringify(data, null, 2));
        loadProducts(); // Refresh products
        loadAISuggestions(); // Refresh suggestions
        loadAnalytics(); // Refresh analytics
        speakResponse({message: "Suggestion executed successfully"});
      } else {
        setError(data.detail || 'Failed to execute suggestion');
      }
    } catch (err) {
      console.error('Failed to execute suggestion:', err);
      setError('Failed to execute suggestion: ' + err.message);
    } finally {
      setExecutingSuggestion(null);
    }
  };

  const processVoiceCommand = async (command) => {
    setLoading(true);
    setError('');
    
    console.log('Processing voice command:', command);
    console.log('Backend URL:', BACKEND_URL);
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/voice-command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command: command,
          language: language
        }),
      });
      
      console.log('Response status:', response.status);
      const data = await response.json();
      console.log('Response data:', data);
      
      if (response.ok) {
        setResponse(JSON.stringify(data, null, 2));
        loadProducts(); // Refresh products list
        loadAISuggestions(); // Refresh AI suggestions
        loadAnalytics(); // Refresh analytics
        
        // Speak the response
        speakResponse(data);
      } else {
        setError(data.detail || 'Command processing failed');
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
    } else if (data.product) {
      const breakdown = data.breakdown;
      textToSpeak = `${data.product} ${data.quantity} kg added at ₹${data.price_per_kg} per kg`;
      
      if (data.low_stock) {
        textToSpeak += '. Low stock alert!';
      }
    } else if (data.products) {
      textToSpeak = `You have ${data.total_products} products in inventory`;
      if (data.low_stock_alerts.length > 0) {
        textToSpeak += `. Warning: ${data.low_stock_alerts.length} products are low in stock`;
      }
    }
    
    if (textToSpeak) {
      // Stop any ongoing speech
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

    if (isListening) {
      return; // Already listening
    }

    setTranscript('');
    setError('');
    setResponse('');
    
    try {
      // Create new recognition instance each time
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = languageConfig[language].code;
      
      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError('');
        console.log('Voice recognition started');
      };
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        console.log('Voice transcript:', transcript);
        console.log('Voice confidence:', event.results[0][0].confidence);
        setTranscript(transcript);
        
        // Process the voice command
        console.log('About to process voice command:', transcript);
         AIprocessVoiceCommand(transcript);
      };
      
      recognitionRef.current.onend = () => {
        setIsListening(false);
        console.log('Voice recognition ended');
      };
      
      recognitionRef.current.onerror = (event) => {
        setError('Voice recognition error: ' + event.error);
        setIsListening(false);
        console.error('Voice recognition error:', event.error);
      };

      recognitionRef.current.start();
    } catch (err) {
      setError('Failed to start voice recognition: ' + err.message);
      setIsListening(false);
      console.error('Voice recognition error:', err);
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
    <div className={`product-card ${product.low_stock ? 'low-stock' : ''}`}>
      <div className="product-header">
        <h3>{product.product}</h3>
        <div className="product-meta">
          <span className="quantity">{product.quantity} kg</span>
          <span className="price">{formatPrice(product.price_per_kg)}/kg</span>
        </div>
      </div>
      
      {product.low_stock && (
        <div className="stock-alert">
          ⚠️ Low Stock Alert
        </div>
      )}
      
      <div className="price-breakdown">
        <div className="breakdown-item">
          <span>1 kg</span>
          <span>{formatPrice(product.breakdown['1kg'])}</span>
        </div>
        <div className="breakdown-item">
          <span>½ kg</span>
          <span>{formatPrice(product.breakdown.half_kg)}</span>
        </div>
        <div className="breakdown-item">
          <span>¼ kg</span>
          <span>{formatPrice(product.breakdown.quarter_kg)}</span>
        </div>
      </div>
    </div>
  );

  const SuggestionCard = ({ suggestion }) => {
    const getPriorityColor = (priority) => {
      if (priority >= 4) return '#ff4444';
      if (priority >= 3) return '#ff8800';
      return '#4CAF50';
    };

    const getPriorityLabel = (priority) => {
      if (priority >= 4) return 'High';
      if (priority >= 3) return 'Medium';
      return 'Low';
    };

    return (
      <div className="suggestion-card">
        <div className="suggestion-header">
          <span className="suggestion-type">{suggestion.type}</span>
          <span 
            className="suggestion-priority"
            style={{ backgroundColor: getPriorityColor(suggestion.priority) }}
          >
            {getPriorityLabel(suggestion.priority)}
          </span>
        </div>
        <div className="suggestion-message">{suggestion.message}</div>
        {suggestion.suggested_action && (
          <div className="suggestion-actions">
            <button
              className="execute-btn"
              onClick={() => executeSuggestion(suggestion.id)}
              disabled={executingSuggestion === suggestion.id || loading}
            >
              {executingSuggestion === suggestion.id ? '⏳ Executing...' : '🚀 Execute'}
            </button>
            <span className="suggested-action">"{suggestion.suggested_action}"</span>
          </div>
        )}
      </div>
    );
  };

  const AnalyticsDashboard = ({ analytics }) => (
    <div className="analytics-dashboard">
      <h3>📊 Analytics Dashboard</h3>
      
      <div className="analytics-summary">
        <div className="metric-card">
          <div className="metric-value">{analytics.summary.total_products}</div>
          <div className="metric-label">Products</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">₹{analytics.summary.total_inventory_value}</div>
          <div className="metric-label">Total Value</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.summary.low_stock_alerts}</div>
          <div className="metric-label">Low Stock</div>
        </div>
        <div className="metric-card">
          <div className="metric-value">{analytics.summary.total_transactions}</div>
          <div className="metric-label">Transactions</div>
        </div>
      </div>

      {Object.keys(analytics.top_products).length > 0 && (
        <div className="analytics-section">
          <h4>🔥 Top Products</h4>
          <div className="top-products">
            {Object.entries(analytics.top_products).slice(0, 5).map(([product, quantity]) => (
              <div key={product} className="top-product-item">
                <span>{product}</span>
                <span>{quantity} kg added</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.keys(analytics.language_usage).length > 0 && (
        <div className="analytics-section">
          <h4>🌐 Language Usage</h4>
          <div className="language-stats">
            {Object.entries(analytics.language_usage).map(([lang, count]) => {
              const langNames = {'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada', 'ta': 'Tamil', 'te': 'Telugu'};
              return (
                <div key={lang} className="language-stat">
                  <span>{langNames[lang] || lang}</span>
                  <span>{count} commands</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎤 AI Voice Catalog</h1>
          <p>Intelligent inventory management with AI suggestions</p>
          <div className="header-actions">
            <button
        {aiSuggestions.length > 0 && (
          <div className="ai-suggestions">
            <div className="section-header">
              <h3>🤖 AI Suggestions</h3>
              <button 
                onClick={loadAISuggestions}
                className="refresh-btn"
                disabled={loading}
              >
                🔄 Refresh
              </button>
            </div>
            <div className="suggestions-grid">
              {aiSuggestions.slice(0, 6).map((suggestion) => (
                <SuggestionCard key={suggestion.id} suggestion={suggestion} />
              ))}
            </div>
          </div>
        )}

        {showAnalytics && analytics && (
          <AnalyticsDashboard analytics={analytics} />
        )}

              className="analytics-toggle"
              onClick={() => setShowAnalytics(!showAnalytics)}
            >
              📊 {showAnalytics ? 'Hide' : 'Show'} Analytics
            </button>
          </div>
        </header>

        <div className="controls">
          <div className="language-selector">
            <select 
              value={language} 
              onChange={(e) => setLanguage(e.target.value)}
              className="language-select"
            >
              {Object.entries(languageConfig).map(([code, config]) => (
                <option key={code} value={code}>{config.name}</option>
              ))}
            </select>
          </div>

          <div className="voice-section">
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={isListening ? stopListening : startListening}
              disabled={loading || !voiceSupported}
            >
              {isListening ? '🛑 Stop' : '🎤 Speak'}
            </button>
            
            {isListening && (
              <div className="listening-indicator">
                <div className="pulse"></div>
                <span>Listening...</span>
              </div>
            )}
          </div>
        </div>

        {transcript && (
          <div className="transcript-section">
            <h3>Voice Command:</h3>
            <div className="transcript">{transcript}</div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {response && (
          <div className="response-section">
            <h3>Response:</h3>
            <pre className="response">{response}</pre>
          </div>
        )}

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <span>Processing...</span>
          </div>
        )}

        <div className="examples">
          <h3>Try saying:</h3>
          <div className="example-commands">
            <div>"Add 5 kg tomato at ₹50"</div>
            <div>"Update tomato price to ₹60"</div>
            <div>"Remove 2 kg onions"</div>
            <div>"List all products"</div>
          </div>
        </div>

        {aiSuggestions.length > 0 && (
          <div className="ai-suggestions">
            <div className="section-header">
              <h3>🤖 AI Suggestions</h3>
              <button 
                onClick={loadAISuggestions}
                className="refresh-btn"
                disabled={loading}
              >
                🔄 Refresh
              </button>
            </div>
            <div className="suggestions-grid">
              {aiSuggestions.slice(0, 6).map((suggestion) => (
                <SuggestionCard key={suggestion.id} suggestion={suggestion} />
              ))}
            </div>
          </div>
        )}

        {showAnalytics && analytics && (
          <AnalyticsDashboard analytics={analytics} />
        )}

        {lowStockAlerts.length > 0 && (
          <div className="stock-alerts">
            <h3>⚠️ Low Stock Alerts</h3>
            <div className="alerts-list">
              {lowStockAlerts.map((product, index) => (
                <div key={index} className="alert-item">
                  <strong>{product.product}</strong> - Only {product.quantity} kg left
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="products-section">
          <div className="section-header">
            <h2>Inventory ({products.length} products)</h2>
            <button 
              onClick={loadProducts}
              className="refresh-btn"
              disabled={loading}
            >
              🔄 Refresh
            </button>
          </div>

          <div className="products-grid">
            {products.length === 0 ? (
              <div className="no-products">
                <p>No products in inventory</p>
                <p>Use voice commands to add products</p>
              </div>
            ) : (
              products.map((product, index) => (
                <ProductCard key={index} product={product} />
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;