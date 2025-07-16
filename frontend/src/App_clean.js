import React, { useState, useEffect, useRef } from 'react';
import './App_clean.css';

const App = () => {
  const [products, setProducts] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [response, setResponse] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [voiceSupported, setVoiceSupported] = useState(false);
  
  const recognitionRef = useRef(null);
  const synthRef = useRef(null);

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
      console.log('Loading products from:', `${BACKEND_URL}/products`);
      const response = await fetch(`${BACKEND_URL}/products`);
      console.log('Products response status:', response.status);
      const data = await response.json();
      console.log('Products data:', data);
      setProducts(data.products || []);
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
    
    console.log('Processing voice command:', command);
    console.log('Backend URL:', BACKEND_URL);
    
    try {
      const response = await fetch(`${BACKEND_URL}/voice-command`, {
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
    } else if (data.success) {
      textToSpeak = 'Command executed successfully';
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
        processVoiceCommand(transcript);
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
      
      <div className="product-category">
        Category: {product.category}
      </div>
    </div>
  );

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎤 Vocal Verse - Voice Inventory Management</h1>
        <p>Manage your inventory with voice commands</p>
      </header>

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
            <ProductCard key={product._id || index} product={product} />
          ))}
        </div>
        
        {products.length === 0 && !loading && (
          <div className="empty-state">
            <p>No products found. Try saying "Add tomato 5 kg at 20 rupees"</p>
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="help-section">
        <h3>Voice Commands Examples:</h3>
        <ul>
          <li>"Add tomato 5 kg at 20 rupees"</li>
          <li>"List all products"</li>
          <li>"Search for tomato"</li>
          <li>"Update tomato price to 25 rupees"</li>
          <li>"Remove tomato"</li>
        </ul>
      </div>
    </div>
  );
};

export default App;