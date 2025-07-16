# ⚡ Quick Deploy to Vercel (5 Minutes)

## 🔥 Option 1: Automated Script
```powershell
# Run the automated deployment script
./deploy-to-vercel.ps1
```

## 🔧 Option 2: Manual Steps

### Step 1: Install Vercel CLI
```powershell
npm install -g vercel
```

### Step 2: Get Required API Keys
- **Gemini API**: [Get key here](https://makersuite.google.com/app/apikey)
- **MongoDB**: [Create free cluster](https://www.mongodb.com/cloud/atlas/register)

### Step 3: Deploy
```powershell
# Login to Vercel
vercel login

# Deploy (from project root)
vercel

# When prompted:
# - Project name: ai-voice-inventory
# - Link to existing: No
# - Directory: ./ (default)
```

### Step 4: Add Environment Variables

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click your project → Settings → Environment Variables
3. Add these variables:

| Variable | Value |
|----------|-------|
| `GEMINI_API_KEY` | your_gemini_api_key |
| `MONGO_URL` | mongodb+srv://user:pass@cluster.mongodb.net/db |

### Step 5: Redeploy
Click "Redeploy" in Vercel dashboard after adding variables.

### Step 6: Test
- Visit your Vercel URL
- Test voice commands
- Check AI suggestions

## 🚨 Common Issues

**Environment variables not working?**
- Redeploy after adding variables
- Check variable names (case-sensitive)

**MongoDB connection fails?**
- Whitelist IP: 0.0.0.0/0
- Check connection string format

**Build errors?**
- Check Vercel function logs
- Ensure all dependencies in requirements.txt

## ✅ Success Checklist
- [ ] Frontend loads
- [ ] Backend API responds at `/api/health`
- [ ] Voice commands work
- [ ] AI suggestions appear
- [ ] Analytics dashboard loads

**🎉 Your AI system is now live!**