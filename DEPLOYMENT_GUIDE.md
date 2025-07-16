# 🚀 Vercel Deployment Guide - AI Voice Inventory Management System

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **MongoDB Atlas Account**: Set up a free cluster at [mongodb.com/atlas](https://mongodb.com/atlas)
3. **Google Gemini API Key**: Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
4. **Git Repository**: Push your code to GitHub, GitLab, or Bitbucket

## 📋 Step-by-Step Deployment

### 1. Prepare Your Environment Variables

First, gather these required environment variables:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/database_name
```

### 2. Deploy to Vercel

#### Option A: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from project root
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Select your account
# - Link to existing project? No
# - Project name: ai-voice-inventory (or your preferred name)
# - In which directory is your code located? ./
```

#### Option B: Deploy via Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure build settings:
   - **Framework Preset**: Other
   - **Root Directory**: ./
   - **Build Command**: `cd frontend && npm run build`
   - **Output Directory**: `frontend/build`
   - **Install Command**: `cd frontend && npm install`

### 3. Configure Environment Variables

In your Vercel project dashboard:

1. Go to **Settings** → **Environment Variables**
2. Add the following variables:

| Name | Value | Environment |
|------|-------|-------------|
| `GEMINI_API_KEY` | your_gemini_api_key | Production, Preview, Development |
| `MONGO_URL` | your_mongodb_connection_string | Production, Preview, Development |

### 4. Update Frontend Environment

Update `frontend/.env.production` with your Vercel URL:

```bash
REACT_APP_BACKEND_URL=https://your-app-name.vercel.app
```

### 5. Configure MongoDB Atlas

1. **Create a Database User**:
   - Go to Database Access
   - Add new database user with read/write permissions

2. **Whitelist IP Addresses**:
   - Go to Network Access
   - Add IP address: `0.0.0.0/0` (allow from anywhere)
   - ⚠️ **Security Note**: For production, restrict to specific IPs

3. **Get Connection String**:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/<database_name>?retryWrites=true&w=majority
   ```

### 6. Test Your Deployment

1. **Backend API**: Visit `https://your-app-name.vercel.app/api/health`
2. **Frontend**: Visit `https://your-app-name.vercel.app`
3. **Voice Commands**: Test the voice functionality
4. **AI Suggestions**: Check if AI suggestions are generated

## 🔧 Configuration Files Explained

### `vercel.json`
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "build" }
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/index.py" },
    { "src": "/(.*)", "dest": "frontend/build/$1" }
  ]
}
```

### `api/index.py`
Entry point for the FastAPI backend on Vercel.

### `requirements.txt`
Python dependencies for the serverless functions.

## 🚨 Common Issues & Solutions

### Issue 1: CORS Errors
**Solution**: Ensure your Vercel URL is added to CORS origins in `backend/server.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: Environment Variables Not Working
**Solution**: 
- Check variable names match exactly
- Redeploy after adding variables
- Verify in Vercel dashboard under Settings → Environment Variables

### Issue 3: API Routes Not Working
**Solution**:
- Ensure `api/index.py` is properly configured
- Check function logs in Vercel dashboard
- Verify Python dependencies in `requirements.txt`

### Issue 4: MongoDB Connection Issues
**Solution**:
- Check connection string format
- Verify database user permissions
- Ensure IP whitelist includes `0.0.0.0/0`

### Issue 5: Build Failures
**Solution**:
- Check build logs in Vercel dashboard
- Ensure all dependencies are listed in `package.json`
- Verify Node.js version compatibility

## 📊 Performance Optimization

### Backend Optimization
- **Function Duration**: Set to 30s max for AI processing
- **Memory**: Default 1024MB should be sufficient
- **Cold Starts**: Consider using Vercel Pro for reduced cold starts

### Frontend Optimization
- **Code Splitting**: Implement React.lazy() for large components
- **Caching**: Leverage Vercel's CDN for static assets
- **Bundle Size**: Monitor and optimize bundle size

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit API keys to version control
2. **CORS**: Restrict origins to your domain in production
3. **MongoDB**: Use specific IP whitelisting instead of 0.0.0.0/0
4. **API Rate Limiting**: Implement rate limiting for production use

## 📈 Monitoring & Analytics

### Vercel Analytics
- Enable in Project Settings → Analytics
- Monitor performance and usage

### Error Tracking
- Use Vercel's function logs for debugging
- Consider integrating Sentry for error tracking

### Performance Monitoring
- Check Core Web Vitals in Vercel dashboard
- Monitor API response times

## 🔄 Continuous Deployment

### Automatic Deployments
Vercel automatically deploys when you push to your main branch.

### Preview Deployments
- Each pull request gets a preview URL
- Test features before merging to main

### Rollback
- Use Vercel dashboard to rollback to previous deployments
- Keep track of deployment history

## 📞 Support Resources

- **Vercel Documentation**: [vercel.com/docs](https://vercel.com/docs)
- **FastAPI on Vercel**: [vercel.com/guides/python](https://vercel.com/guides/python)
- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com/)

## 🎉 Success Checklist

- [ ] Environment variables configured
- [ ] MongoDB Atlas connected
- [ ] Frontend builds successfully
- [ ] Backend API responds
- [ ] Voice commands work
- [ ] AI suggestions generate
- [ ] Analytics dashboard loads
- [ ] Mobile responsiveness tested

Your AI-powered voice inventory management system should now be live on Vercel! 🚀