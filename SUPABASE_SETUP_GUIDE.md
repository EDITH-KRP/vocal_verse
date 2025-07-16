# 🚀 Supabase Integration Setup Guide

This guide will help you set up Supabase for authentication, database storage, and analytics for the Vocal Verse application.

## 📋 Prerequisites

1. A Supabase account (sign up at https://supabase.com)
2. Node.js and npm/yarn installed
3. The Vocal Verse project files

## 🔧 Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Choose your organization
4. Fill in project details:
   - **Name**: `vocal-verse` (or your preferred name)
   - **Database Password**: Create a strong password
   - **Region**: Choose closest to your location
5. Click "Create new project"
6. Wait for the project to be set up (usually 2-3 minutes)

## 🗄️ Step 2: Set Up Database Schema

1. In your Supabase dashboard, go to the **SQL Editor**
2. Copy the contents of `backend/supabase_schema.sql`
3. Paste it into the SQL Editor
4. Click **Run** to execute the schema creation
5. Verify tables are created in the **Table Editor**

Expected tables:
- `users` - User authentication and profiles
- `products` - Inventory products
- `inventory_transactions` - Transaction history
- `voice_commands` - Voice command logs
- `user_preferences` - User settings
- `stock_alerts` - Low stock notifications
- `market_trends` - Price trend data

## 🔑 Step 3: Get API Keys

1. In your Supabase dashboard, go to **Settings** → **API**
2. Copy the following values:
   - **Project URL** (e.g., `https://your-project.supabase.co`)
   - **anon public key** (starts with `eyJ...`)
   - **service_role secret key** (starts with `eyJ...`)

## ⚙️ Step 4: Configure Environment Variables

### Backend Configuration

1. Create a `.env` file in the `backend/` directory:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# JWT Configuration
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Configuration (optional)
GEMINI_API_KEY=your_gemini_api_key_here

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

### Frontend Configuration

1. Create a `.env` file in the `frontend/` directory:

```bash
# Backend API
REACT_APP_BACKEND_URL=http://localhost:8000

# Supabase Configuration
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your_anon_key_here
```

## 📦 Step 5: Install Dependencies

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Frontend Dependencies

```bash
cd frontend
npm install
# or
yarn install
```

## 🚀 Step 6: Start the Application

### Start Backend Server

```bash
cd backend
python supabase_server.py
```

The backend will start on `http://localhost:8000`

### Start Frontend Server

```bash
cd frontend
npm start
# or
yarn start
```

The frontend will start on `http://localhost:3000`

## 🔐 Step 7: Configure Row Level Security (RLS)

The schema automatically sets up RLS policies, but verify they're active:

1. Go to **Authentication** → **Policies** in Supabase dashboard
2. Ensure policies are enabled for all tables
3. Test by creating a user account in your app

## 🧪 Step 8: Test the Integration

1. Open `http://localhost:3000` in your browser
2. Register a new account
3. Login with your credentials
4. Test voice commands:
   - "Add tomato 5 kg at 20 rupees"
   - "List all products"
   - "Predict tomato stock for 7 days"
5. Check the Analytics dashboard
6. Verify data appears in Supabase dashboard

## 📊 Step 9: Enable Analytics Features

### Set up Real-time Subscriptions (Optional)

1. In Supabase dashboard, go to **Database** → **Replication**
2. Enable replication for tables you want real-time updates:
   - `products`
   - `inventory_transactions`
   - `stock_alerts`

### Configure Storage (Optional)

If you want to store product images:

1. Go to **Storage** in Supabase dashboard
2. Create a bucket named `product-images`
3. Set appropriate policies for image uploads

## 🔧 Advanced Configuration

### Custom Domain (Production)

1. Go to **Settings** → **Custom Domains**
2. Add your domain
3. Update environment variables with new URL

### Email Templates

1. Go to **Authentication** → **Email Templates**
2. Customize registration and password reset emails

### Database Backups

1. Go to **Settings** → **Database**
2. Enable automated backups
3. Set backup retention period

## 🐛 Troubleshooting

### Common Issues

1. **Connection Error**: Check if Supabase URL and keys are correct
2. **Authentication Failed**: Verify JWT secret key is set
3. **Database Error**: Ensure schema was created successfully
4. **CORS Issues**: Check if frontend URL is in allowed origins

### Debug Mode

Enable debug logging by setting:

```bash
# Backend
DEBUG=true

# Frontend
REACT_APP_DEBUG=true
```

### Check Logs

- **Backend logs**: Check terminal where `supabase_server.py` is running
- **Frontend logs**: Check browser console (F12)
- **Supabase logs**: Go to **Logs** in Supabase dashboard

## 📈 Features Enabled

With Supabase integration, you now have:

✅ **User Authentication**
- Registration and login
- JWT-based sessions
- Password reset functionality

✅ **Secure Database Storage**
- All inventory data stored in PostgreSQL
- Row-level security
- Real-time updates

✅ **Advanced Analytics**
- Consumption rate analysis
- Stock depletion predictions
- Low stock alerts
- Interactive dashboards

✅ **Voice Command History**
- All commands logged
- Success/failure tracking
- Usage analytics

✅ **Predictive Features**
- Stock forecasting
- Reorder suggestions
- Trend analysis

## 🎯 Next Steps

1. **Customize Analytics**: Modify prediction algorithms in `supabase_server.py`
2. **Add More Features**: Implement supplier management, purchase orders
3. **Mobile App**: Use Supabase's mobile SDKs for React Native
4. **API Integration**: Connect to external inventory systems
5. **Reporting**: Generate PDF reports using the analytics data

## 📞 Support

If you encounter issues:

1. Check the [Supabase Documentation](https://supabase.com/docs)
2. Review error logs in both backend and Supabase dashboard
3. Ensure all environment variables are correctly set
4. Verify database schema was created successfully

---

## 🎉 Congratulations!

Your Vocal Verse application now has:
- Secure user authentication
- Cloud database storage
- Advanced analytics and predictions
- Real-time inventory management
- Voice-powered interface with data persistence

Start managing your inventory with voice commands and get intelligent insights about your stock levels!