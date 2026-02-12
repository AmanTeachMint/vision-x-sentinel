# Deploy Vision X Sentinel on Vercel

Complete guide to deploy both frontend and backend on Vercel.

## Overview

- **Frontend**: Deploy React/Vite app on Vercel
- **Backend**: Deploy Flask app as serverless function on Vercel
- **Database**: Use MongoDB Atlas (free tier)

---

## Prerequisites

1. GitHub account
2. Vercel account ([vercel.com](https://vercel.com))
3. MongoDB Atlas account ([mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas))

---

## Step 1: Setup MongoDB Atlas

1. **Create Account**: Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

2. **Create Free Cluster**:
   - Click "Build a Database"
   - Choose **FREE** (M0) tier
   - Select region closest to you
   - Create cluster (takes 3-5 minutes)

3. **Create Database User**:
   - Go to "Database Access" → "Add New Database User"
   - Username: `vision-sentinel` (or your choice)
   - Password: Generate secure password (save it!)
   - Database User Privileges: "Read and write to any database"

4. **Whitelist IP Addresses**:
   - Go to "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" (for demo) or add `0.0.0.0/0`
   - Or add specific IPs for production

5. **Get Connection String**:
   - Go to "Clusters" → Click "Connect"
   - Choose "Connect your application"
   - Copy the connection string
   - Replace `<password>` with your database user password
   - Example: `mongodb+srv://vision-sentinel:yourpassword@cluster0.xxxxx.mongodb.net/`

---

## Step 2: Prepare Backend for Vercel

The backend is already configured! Files created:
- ✅ `backend/vercel.json` - Vercel configuration
- ✅ `backend/api/index.py` - Serverless function entry point

### Update Environment Variables

You'll set these in Vercel dashboard, but here's what you need:

```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB_NAME=vision_x_sentinel
CORS_ORIGIN=https://your-frontend.vercel.app
```

---

## Step 3: Deploy Backend on Vercel

### Option A: Deploy via Vercel Dashboard

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Import Project**:
   - Click "Add New Project"
   - Import your GitHub repository
   - Select the repository

3. **Configure Project**:
   - **Root Directory**: Set to `backend`
   - **Framework Preset**: Other (or leave blank)
   - **Build Command**: Leave empty (Vercel auto-detects Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables**:
   Add these in Vercel dashboard:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB_NAME=vision_x_sentinel
   CORS_ORIGIN=https://your-frontend.vercel.app
   ```
   (You'll update CORS_ORIGIN after frontend deploys)

5. **Deploy**: Click "Deploy"

6. **Get Backend URL**: 
   - After deployment, Vercel provides URL like: `https://your-backend.vercel.app`
   - Note this URL - you'll need it for frontend

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to backend
cd backend

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add MONGO_URI
vercel env add MONGO_DB_NAME
vercel env add CORS_ORIGIN

# Deploy to production
vercel --prod
```

---

## Step 4: Seed Database

After backend is deployed, seed the database:

### Option A: Run Locally (Pointing to Atlas)

1. **Update local `.env`**:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB_NAME=vision_x_sentinel
   ```

2. **Run seed script**:
   ```bash
   cd backend
   source venv/bin/activate
   python scripts/seed_db.py
   ```

### Option B: Use Vercel Function (Create API endpoint)

Create a one-time seed endpoint or use MongoDB Compass to import data.

---

## Step 5: Update Frontend API Configuration

### Update API Client

Edit `frontend/src/api/client.js`:

**Change line 2:**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**To:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

### Create Environment File

Create `frontend/.env.production`:
```env
VITE_API_URL=https://your-backend.vercel.app/api
```

**Note**: Replace `your-backend.vercel.app` with your actual Vercel backend URL.

---

## Step 6: Deploy Frontend on Vercel

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Add New Project**:
   - Click "Add New Project"
   - Import your GitHub repository (same repo)
   - Select the repository

3. **Configure Project**:
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Environment Variables**:
   Add:
   ```
   VITE_API_URL=https://your-backend.vercel.app/api
   ```
   (Use the backend URL from Step 3)

5. **Deploy**: Click "Deploy"

6. **Get Frontend URL**: 
   - Vercel provides URL like: `https://your-frontend.vercel.app`

---

## Step 7: Update Backend CORS

After frontend deploys, update backend CORS:

1. Go to Vercel Dashboard → Your Backend Project
2. Go to "Settings" → "Environment Variables"
3. Update `CORS_ORIGIN` to your frontend URL:
   ```
   CORS_ORIGIN=https://your-frontend.vercel.app
   ```
4. Redeploy backend (or it will auto-redeploy)

---

## Step 8: Verify Deployment

### Test Backend
```bash
# Health check
curl https://your-backend.vercel.app/

# Get classrooms
curl https://your-backend.vercel.app/api/classrooms
```

### Test Frontend
- Open `https://your-frontend.vercel.app`
- Check browser console for errors
- Verify API calls are working

---

## Project Structure for Vercel

```
vision-x-sentinel/
├── backend/
│   ├── api/
│   │   └── index.py          # Vercel serverless entry point
│   ├── app/
│   │   ├── main.py           # Flask app
│   │   └── ...
│   ├── vercel.json           # Vercel config
│   └── requirements.txt
└── frontend/
    ├── src/
    ├── .env.production       # Frontend env vars
    └── package.json
```

---

## Important Notes

### Vercel Serverless Limitations

1. **Function Timeout**: 
   - Hobby plan: 10 seconds
   - Pro plan: 60 seconds
   - Your frame analysis should complete within this

2. **Cold Starts**: 
   - First request may be slow (~1-2 seconds)
   - Subsequent requests are fast

3. **File Storage**:
   - Vercel functions are stateless
   - Use MongoDB for data storage
   - Video files should be in frontend `public/` folder

4. **Environment Variables**:
   - Set in Vercel dashboard
   - Available at runtime via `os.getenv()`

### MongoDB Atlas Considerations

- **Free Tier Limits**: 512MB storage, shared cluster
- **Connection Limits**: 500 connections
- **Suitable for**: Demo, small-scale production
- **Upgrade needed**: For high traffic

---

## Troubleshooting

### Backend Not Deploying

**Error: Module not found**
- Check `requirements.txt` includes all dependencies
- Verify Python version (Vercel uses Python 3.9+)

**Error: Import errors**
- Check `api/index.py` path setup
- Verify `app/` directory structure

### CORS Errors

- Verify `CORS_ORIGIN` matches frontend URL exactly
- Include `https://` protocol
- No trailing slash

### API Connection Failed

- Check `VITE_API_URL` in frontend environment variables
- Verify backend URL is correct
- Check browser console for errors

### MongoDB Connection Failed

- Verify connection string format
- Check IP whitelist in Atlas
- Verify database user credentials
- Check network access settings

---

## Quick Deployment Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Database user created
- [ ] IP whitelisted in Atlas
- [ ] Backend code pushed to GitHub
- [ ] Backend deployed on Vercel
- [ ] Backend environment variables set
- [ ] Database seeded
- [ ] Frontend API client updated
- [ ] Frontend `.env.production` created
- [ ] Frontend deployed on Vercel
- [ ] Frontend environment variables set
- [ ] Backend CORS updated with frontend URL
- [ ] Both apps tested and working

---

## Cost

**Vercel Hobby Plan (Free)**:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Serverless functions
- ✅ Perfect for demo

**MongoDB Atlas Free Tier**:
- ✅ 512MB storage
- ✅ Shared cluster
- ✅ Perfect for demo

**Total Cost: $0/month** 🎉

---

## Next Steps

1. Deploy backend → Get URL
2. Deploy frontend → Get URL  
3. Update CORS → Test
4. Share demo URLs!

Your demo will be live at:
- Frontend: `https://your-frontend.vercel.app`
- Backend API: `https://your-backend.vercel.app/api`
