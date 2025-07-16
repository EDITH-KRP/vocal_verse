# 🚀 Vercel Deployment - Step by Step

## ✅ Pre-Deployment Checklist

### 1. Accounts You Need:
- [ ] **Vercel Account** - [Sign up here](https://vercel.com/signup)
- [ ] **GitHub Account** - [Sign up here](https://github.com/signup)
- [ ] **MongoDB Atlas** - [Sign up here](https://www.mongodb.com/cloud/atlas/register)
- [ ] **Google AI Studio** - [Get Gemini API Key](https://makersuite.google.com/app/apikey)

### 2. Tools Installation:
```powershell
# Install Node.js (if not installed)
# Download from: https://nodejs.org/

# Install Git (if not installed)
# Download from: https://git-scm.com/

# Install Vercel CLI
npm install -g vercel
```

---

## 🔧 STEP 1: Prepare Your Environment Variables

### Create MongoDB Atlas Database:

1. **Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)**
2. **Create a new project** → Click "Create Project"
3. **Build a database** → Choose "Free" tier
4. **Create cluster** → Choose your region
5. **Create database user:**
   - Go to "Database Access"
   - Click "Add New Database User"
   - Choose "Password" authentication
   - Username: `admin` (or your choice)
   - Password: Generate a secure password
   - Database User Privileges: "Read and write to any database"
6. **Add IP address:**
   - Go to "Network Access"
   - Click "Add IP Address"
   - Choose "Allow access from anywhere" (0.0.0.0/0)
   - Click "Confirm"
7. **Get connection string:**
   - Go to "Database" → "Connect" → "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your actual password

### Get Google Gemini API Key:

1. **Go to [Google AI Studio](https://makersuite.google.com/app/apikey)**
2. **Click "Create API Key"**
3. **Copy the generated API key**

### Create .env file:
```bash
# Create .env file in your project root
GEMINI_API_KEY=your_actual_gemini_api_key_here
MONGO_URL=mongodb+srv://admin:yourpassword@cluster0.xxxxx.mongodb.net/voice_inventory?retryWrites=true&w=majority
```

---

## 🔧 STEP 2: Test Locally (Optional but Recommended)

```powershell
# Run the setup check
python deploy-check.py

# Start backend (in one terminal)
cd backend
python server.py

# Start frontend (in another terminal)
cd frontend
npm start
```

Visit `http://localhost:3000` to test everything works.

---

## 📁 STEP 3: Push to GitHub

### Initialize Git repository:
```powershell
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Voice Inventory Management System"

# Create repository on GitHub:
# 1. Go to github.com
# 2. Click "New repository"
# 3. Name it: "ai-voice-inventory" 
# 4. Make it Public
# 5. Don't initialize with README (we already have files)
# 6. Click "Create repository"

# Add remote origin (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/ai-voice-inventory.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🚀 STEP 4: Deploy to Vercel

### Method A: Via Vercel Dashboard (Recommended)

1. **Go to [Vercel Dashboard](https://vercel.com/dashboard)**

2. **Click "New Project"**

3. **Import Git Repository:**
   - Find your GitHub repository
   - Click "Import"

4. **Configure Project:**
   - **Project Name:** `ai-voice-inventory` (or your choice)
   - **Framework Preset:** Other
   - **Root Directory:** `./` (leave as default)
   - **Build Command:** Leave empty (Vercel will use vercel.json)
   - **Output Directory:** Leave empty
   - **Install Command:** Leave empty

5. **Click "Deploy"**

### Method B: Via Vercel CLI

```powershell
# Login to Vercel
vercel login

# Navigate to your project directory
cd C:\Users\prajw\Downloads\EDITH-AI-vocal\EDITH-AI-vocal

# Deploy
vercel

# Follow the prompts:
# ? Set up and deploy "C:\Users\prajw\Downloads\EDITH-AI-vocal\EDITH-AI-vocal"? [Y/n] Y
# ? Which scope do you want to deploy to? [Use your account]
# ? Link to existing project? [y/N] N
# ? What's your project's name? ai-voice-inventory
# ? In which directory is your code located? ./

# The deployment will start automatically
```

---

## ⚙️ STEP 5: Configure Environment Variables in Vercel

1. **Go to your project in Vercel Dashboard**

2. **Click "Settings" tab**

3. **Click "Environment Variables" in sidebar**

4. **Add these variables:**

   | Variable Name | Value | Environments |
   |---------------|-------|-------------|
   | `GEMINI_API_KEY` | your_actual_gemini_api_key | Production, Preview, Development |
   | `MONGO_URL` | your_mongodb_connection_string | Production, Preview, Development |

5. **Click "Add" for each variable**

6. **Redeploy:**
   - Go to "Deployments" tab
   - Click "..." next to latest deployment
   - Click "Redeploy"

---

## 🔧 STEP 6: Update Frontend URL

1. **Note your Vercel URL** (e.g., `https://ai-voice-inventory-abc123.vercel.app`)

2. **Update frontend environment:**
   ```bash
   # Edit frontend/.env.production
   REACT_APP_BACKEND_URL=https://your-actual-vercel-url.vercel.app
   ```

3. **Commit and push changes:**
   ```powershell
   git add frontend/.env.production
   git commit -m "Update production backend URL"
   git push
   ```

4. **Vercel will automatically redeploy**

---

## 🧪 STEP 7: Test Your Deployment

### Test Backend API:
Visit: `https://your-app-name.vercel.app/api/health`

Expected response:
```json
{
  "status": "healthy",
  "message": "AI Voice Inventory Management API is running",
  "timestamp": "2024-01-XX...",
  "version": "1.0.0"
}
```

### Test Frontend:
Visit: `https://your-app-name.vercel.app`

### Test Voice Commands:
1. Click the microphone button
2. Say: "Add 5 kg tomato at 50 rupees"
3. Check if it processes correctly

### Test AI Features:
1. Click "Show Analytics" button
2. Check if AI suggestions appear
3. Try executing a suggestion

---

## 🚨 Troubleshooting Common Issues

### Issue 1: "Function exceeded maximum duration"
**Solution:** 
- The AI processing might take time
- Gemini API might be slow
- This is normal for the first few requests (cold start)

### Issue 2: "CORS errors"
**Solution:**
```python
# Already configured in server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 3: "MongoDB connection failed"
**Solutions:**
- Check your MongoDB connection string
- Ensure IP 0.0.0.0/0 is whitelisted
- Verify database user has correct permissions
- Test connection string in MongoDB Compass

### Issue 4: "Gemini API errors"
**Solutions:**
- Verify API key is correct
- Check if you have API quota remaining
- Ensure the API key has proper permissions

### Issue 5: "Environment variables not working"
**Solutions:**
- Check variable names are exact (case-sensitive)
- Redeploy after adding variables
- Check in Vercel dashboard under Settings → Environment Variables

---

## 📊 Monitor Your Deployment

### Vercel Analytics:
1. Go to your project dashboard
2. Click "Analytics" tab
3. Monitor performance and usage

### Function Logs:
1. Go to "Functions" tab
2. Click on any function to see logs
3. Monitor for errors or performance issues

### Performance:
- Check Core Web Vitals
- Monitor API response times
- Watch for cold start issues

---

## 🎉 Success Checklist

After deployment, verify these work:

- [ ] **Frontend loads** at your Vercel URL
- [ ] **Backend API responds** at `/api/health`
- [ ] **Voice recognition works** (browser permissions)
- [ ] **Voice commands process** successfully
- [ ] **Products list/add/update** functionality
- [ ] **AI suggestions appear** and can be executed
- [ ] **Analytics dashboard** shows data
- [ ] **Multi-language support** works
- [ ] **Mobile responsive** design works

---

## 🔄 Future Updates

To update your deployment:

```powershell
# Make changes to your code
# Commit and push to GitHub
git add .
git commit -m "Your update message"
git push

# Vercel automatically redeploys on push to main branch
```

---

## 📞 Get Help

If you encounter issues:

1. **Check Vercel logs:** Go to Functions tab in your dashboard
2. **Check this guide:** All common issues are covered above
3. **Vercel docs:** [vercel.com/docs](https://vercel.com/docs)
4. **MongoDB docs:** [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com/)

---

**🎯 Your AI-powered voice inventory system is now live on Vercel!**