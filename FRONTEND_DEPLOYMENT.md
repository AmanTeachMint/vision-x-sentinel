# Frontend Deployment Guide - Vercel

## Step-by-Step Frontend Deployment

### Prerequisites
- ✅ Backend deployed on Vercel (you should have backend URL)
- ✅ Backend URL: `https://your-backend-name.vercel.app`

---

## Step 1: Update Frontend API Client

First, update the frontend to use environment variables for the API URL.

### Edit `frontend/src/api/client.js`

**Change line 2 from:**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**To:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

This allows the frontend to use the backend URL from environment variables.

---

## Step 2: Commit and Push Changes

```bash
# Make sure you're in the project root
cd /Users/aman/Desktop/manu2/vision-x-sentinel

# Check what files changed
git status

# Add changes
git add frontend/src/api/client.js

# Commit
git commit -m "Update API client to use environment variables for Vercel deployment"

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy Frontend on Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Add New Project**:
   - Click **"Add New Project"** (top right)
   - Click **"Import Git Repository"**
   - Select your `vision-x-sentinel` repository
   - Click **"Import"**

3. **Configure Project**:
   - **Root Directory**: Click **"Edit"** → Set to `frontend`
   - **Framework Preset**: Should auto-detect as **"Vite"** (if not, select "Vite")
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)
   - **Install Command**: `npm install` (auto-detected)

4. **Environment Variables** (IMPORTANT!):
   Click **"Environment Variables"** to expand, then add:
   
   ```
   Name: VITE_API_URL
   Value: https://your-backend-name.vercel.app/api
   ```
   
   **Replace `your-backend-name.vercel.app` with your actual backend URL!**
   
   Example:
   ```
   VITE_API_URL=https://vision-x-sentinel-backend.vercel.app/api
   ```

5. **Deploy**:
   - Click **"Deploy"** button
   - Wait 2-3 minutes for build

6. **Get Frontend URL**:
   - After deployment: `https://your-frontend-name.vercel.app`
   - **Save this URL!**

---

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI (if not installed)
npm install -g vercel

# Navigate to frontend
cd frontend

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variable
vercel env add VITE_API_URL
# Paste: https://your-backend-name.vercel.app/api

# Deploy to production
vercel --prod
```

---

## Step 4: Update Backend CORS

After frontend deploys, update backend CORS to allow your frontend URL:

1. **Go to Vercel Dashboard** → Your **Backend Project**

2. **Go to Settings** → **Environment Variables**

3. **Update `CORS_ORIGIN`**:
   - Find `CORS_ORIGIN` variable
   - Change value from `*` to your frontend URL:
   ```
   https://your-frontend-name.vercel.app
   ```
   - Click **"Save"**

4. **Redeploy Backend** (or it will auto-redeploy):
   - Go to **"Deployments"** tab
   - Click **"Redeploy"** on latest deployment
   - Or wait for auto-redeploy

---

## Step 5: Verify Deployment

### Test Frontend:
1. **Open Frontend URL**: `https://your-frontend-name.vercel.app`
2. **Check Browser Console** (F12):
   - Should see no CORS errors
   - API calls should go to your backend
3. **Test Features**:
   - Classrooms should load
   - Videos should play
   - Frame analysis should work
   - Alerts should appear

### Test API Connection:
Open browser console and check:
- Network tab should show API calls to: `https://your-backend-name.vercel.app/api/...`
- No CORS errors
- Data loads correctly

---

## Troubleshooting

### Error: "Failed to fetch classrooms"

**Cause**: Frontend can't reach backend

**Fix**:
1. Check `VITE_API_URL` is set correctly in Vercel
2. Verify backend URL is correct
3. Check backend is deployed and running
4. Verify CORS_ORIGIN in backend matches frontend URL

### Error: CORS Error

**Cause**: Backend CORS not configured for frontend URL

**Fix**:
1. Update `CORS_ORIGIN` in backend environment variables
2. Set to: `https://your-frontend-name.vercel.app`
3. Redeploy backend

### Error: "Module not found" or Build Errors

**Cause**: Dependencies not installed

**Fix**:
1. Check `package.json` exists in `frontend/` directory
2. Verify `npm install` runs during build
3. Check build logs in Vercel dashboard

### Frontend Shows "Loading..." Forever

**Cause**: API calls failing

**Fix**:
1. Check browser console for errors
2. Verify `VITE_API_URL` environment variable is set
3. Test backend URL directly: `https://your-backend-name.vercel.app/api/classrooms`
4. Check network tab in browser dev tools

---

## Quick Checklist

- [ ] Frontend API client updated (`import.meta.env.VITE_API_URL`)
- [ ] Changes committed and pushed to GitHub
- [ ] Frontend deployed on Vercel
- [ ] Root Directory set to `frontend`
- [ ] Framework Preset: Vite
- [ ] Environment variable `VITE_API_URL` set with backend URL
- [ ] Frontend URL obtained
- [ ] Backend `CORS_ORIGIN` updated with frontend URL
- [ ] Backend redeployed (if needed)
- [ ] Frontend tested and working

---

## Your URLs Summary

After deployment:

- **Backend API**: `https://your-backend-name.vercel.app`
- **Frontend**: `https://your-frontend-name.vercel.app`
- **Frontend Environment Variable**: `VITE_API_URL=https://your-backend-name.vercel.app/api`
- **Backend Environment Variable**: `CORS_ORIGIN=https://your-frontend-name.vercel.app`

---

## Important Notes

1. **Environment Variables**:
   - Frontend uses `VITE_` prefix (required for Vite)
   - Backend uses `CORS_ORIGIN` without prefix

2. **CORS**:
   - Must match exactly (including `https://`)
   - No trailing slash

3. **Auto-Deploy**:
   - Vercel auto-deploys on every push to GitHub
   - Update environment variables in Vercel dashboard (not in code)

4. **Build Time**:
   - Frontend build takes 1-3 minutes
   - Backend build takes 2-5 minutes

---

**You're ready to deploy! Follow the steps above and your frontend will be live!** 🚀
