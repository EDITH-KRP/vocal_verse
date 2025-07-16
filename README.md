# 🎤 AI-Powered Voice Inventory Management System

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/ai-voice-inventory)

A revolutionary inventory management system powered by AI voice commands, intelligent suggestions, and real-time analytics. Built with FastAPI, React, and Google Gemini AI.

## ✨ Key Features

- 🎤 **Voice Commands**: Add, update, remove inventory using natural speech
- 🌍 **Multilingual Support**: English, Hindi, Kannada, Tamil, Telugu
- 🤖 **AI Suggestions**: Smart recommendations for inventory optimization
- 📊 **Real-time Analytics**: Trend analysis and predictive insights
- 🔄 **Smart Merging**: Automatic inventory consolidation with price averaging
- 📱 **Responsive Design**: Works on desktop and mobile devices

## 🚀 Quick Deploy to Vercel

### One-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/yourusername/ai-voice-inventory)

### Manual Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/ai-voice-inventory.git
cd ai-voice-inventory

# Run setup script (Windows)
./setup-deployment.ps1

# Or setup manually
cd frontend && npm install
cd .. && pip install -r requirements.txt

# Deploy to Vercel
vercel
```

## 📋 Prerequisites

- **Node.js** 16+ 
- **Python** 3.8+
- **Google Gemini API Key** ([Get here](https://makersuite.google.com/app/apikey))
- **MongoDB Atlas Account** ([Sign up](https://mongodb.com/atlas))

## 🔧 Local Development

### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file
GEMINI_API_KEY=your_gemini_api_key
MONGO_URL=your_mongodb_connection_string

# Start server
python server.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Test AI Features
```bash
python backend/test_ai_system.py
```

## 📖 Documentation

- **[Deployment Guide](./DEPLOYMENT_GUIDE.md)** - Complete Vercel deployment instructions
- **[AI Features Guide](./backend/AI_FEATURES_README.md)** - Detailed AI capabilities overview
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running locally)

## 🌟 Demo

Try these voice commands:
- "Add 5 kg tomato at 50 rupees"
- "5 किलो टमाटर 50 रुपये में जोड़ो" (Hindi)
- "5 ಕಿಲೋ ಟೊಮೇಟೊ 50 ರೂಪಾಯಿ ಸೇರಿಸಿ" (Kannada)
- "Update tomato price to 60"
- "List all products"

## 🤖 AI Capabilities

### Smart Product Merging
- Automatically merges duplicate products
- Calculates weighted average prices
- Maintains inventory accuracy

### Voice Processing
- Natural language understanding
- Multi-language support
- Intent recognition and extraction

### Analytics & Insights
- Real-time trend analysis
- Statistical confidence scoring
- Predictive modeling

### Intelligent Suggestions
- Low stock alerts
- Price optimization recommendations
- Trend-based insights
- AI-powered inventory optimization

## 📊 Tech Stack

- **Backend**: FastAPI, Python, Google Gemini AI
- **Frontend**: React, JavaScript, Web Speech API
- **Database**: MongoDB Atlas
- **Analytics**: Pandas, NumPy, SciPy
- **Deployment**: Vercel
- **AI**: Google Generative AI

## 🔐 Environment Variables

```bash
# Required for deployment
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database

# Frontend (development)
REACT_APP_BACKEND_URL=http://localhost:8000
```

## 🛠️ Development Tools

- **Pre-deployment Check**: `python deploy-check.py`
- **Setup Script**: `./setup-deployment.ps1`
- **AI Demo**: `python backend/test_ai_system.py`

## 📈 Performance Features

- **Background Processing**: Automatic AI suggestion generation
- **Caching**: Intelligent response caching
- **Optimization**: Bundle splitting and lazy loading
- **Analytics**: Real-time performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python backend/test_ai_system.py`
5. Submit a pull request

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-voice-inventory/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-voice-inventory/discussions)
- **Documentation**: [AI Features Guide](./backend/AI_FEATURES_README.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Roadmap

- [ ] Computer Vision integration
- [ ] IoT sensor support
- [ ] Mobile app (React Native)
- [ ] Advanced ML models
- [ ] Market price integration
- [ ] Multi-tenant support

---

**Built with ❤️ using modern AI technologies**
