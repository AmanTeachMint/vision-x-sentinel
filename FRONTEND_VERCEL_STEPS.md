# Frontend Deployment Steps - Vercel

## ✅ Pre-Deployment Checklist

- [x] API client updated to use `VITE_API_URL` environment variable
- [ ] Backend deployed and URL obtained
- [ ] Code committed and pushed to GitHub

---

## Step 1: Get Your Backend URL

Before deploying frontend, make sure you have your backend URL from Vercel:

**Backend URL Format**: `https://your-backend-name.vercel.app`

**Example**: `https://vision-x-sentinel-backend.vercel.app`

**API Base URL**: `https://your-backend-name.vercel.app/api`

---

## Step 2: Commit and Push Frontend Changes

Make sure the API client update is committed:

```bash
cd /Users/aman/Desktop/manu2/vision-x-sentinel

# Check status
git status

# Add changes
git add frontend/src/api/client.js

# Commit
git commit -m "Update frontend API client for Vercel deployment"

# Push to GitHub
git push origin main
```

---

## Step 3: Deploy Frontend on Vercel

### Via Vercel Dashboard:

1. **Go to Vercel Dashboard**: [vercel.com/dashboard](https://vercel.com/dashboard)

2. **Add New Project**:
   - Click **"Add New Project"** (top right)
   - Click **"Import Git Repository"**
   - Select your `vision-x-sentinel` repository
   - Click **"Import"**

3. **Configure Project**:
   - **Root Directory**: Click **"Edit"** → Set to `frontend`
   - **Framework Preset**: Should auto-detect as **"Vite"** ✅
   - **Build Command**: `npm run build` (auto-detected) ✅
   - **Output Directory**: `dist` (auto-detected) ✅
   - **Install Command**: `npm install` (auto-detected) ✅

4. **Environment Variables** (CRITICAL!):
   - Click **"Environment Variables"** to expand
   - Click **"Add"** or **"Add Another"**
   - Add this variable:
     ```
     Name: VITE_API_URL
     Value: https://your-backend-name.vercel.app/api
     ```
   - **Replace `your-backend-name.vercel.app` with your actual backend URL!**
   - Example:
     ```
     VITE_API_URL=https://vision-x-sentinel-backend.vercel.app/api
     ```
   - Make sure to select **"Production"**, **"Preview"**, and **"Development"** environments
   - Click **"Save"**

5. **Deploy**:
   - Click **"Deploy"** button
   - Wait 2-3 minutes for build to complete

6. **Get Frontend URL**:
   - After deployment completes, Vercel shows: `https://your-frontend-name.vercel.app`
   - **Save this URL!**

---

## Step 4: Update Backend CORS

After frontend deploys successfully:

1. **Go to Vercel Dashboard** → Your **Backend Project**

2. **Settings** → **Environment Variables**

3. **Find `CORS_ORIGIN`** variable:
   - Current value might be `*`
   - Click **"Edit"** or update it

4. **Update Value**:
   ```
   https://your-frontend-name.vercel.app
   ```
   - Replace with your actual frontend URL
   - **Important**: Include `https://` but NO trailing slash
   - Example: `https://vision-x-sentinel-frontend.vercel.app`

5. **Save**:
   - Click **"Save"**
   - Backend will auto-redeploy (or manually redeploy)

---

## Step 5: Verify Deployment

### Test Frontend:

1. **Open Frontend URL**: `https://your-frontend-name.vercel.app`

2. **Open Browser DevTools** (F12):
   - Go to **Console** tab
   - Check for errors
   - Should see no CORS errors

3. **Check Network Tab**:
   - Go to **Network** tab
   - Refresh page
   - Look for API calls to: `https://your-backend-name.vercel.app/api/...`
   - Should return 200 OK status

4. **Test Features**:
   - ✅ Classrooms should load
   - ✅ Videos should play
   - ✅ Frame analysis should work
   - ✅ Alerts should appear

---

## Troubleshooting

### Error: "Failed to fetch classrooms"

**Cause**: Frontend can't reach backend

**Fix**:
1. Check `VITE_API_URL` is set correctly in Vercel
2. Verify backend URL is correct (test in browser)
3. Check backend is deployed and running
4. Verify CORS_ORIGIN in backend matches frontend URL exactly

### Error: CORS Error

**Cause**: Backend CORS not configured for frontend URL

**Fix**:
1. Update `CORS_ORIGIN` in backend environment variables
2. Set to: `https://your-frontend-name.vercel.app` (exact match)
3. No trailing slash, include `https://`
4. Redeploy backend

### Error: Build Failed

**Cause**: Dependencies or build issues

**Fix**:
1. Check build logs in Vercel dashboard
2. Verify `package.json` exists in `frontend/` directory
3. Check `npm install` runs successfully
4. Verify `npm run build` works locally

### Frontend Shows "Loading..." Forever

**Cause**: API calls failing

**Fix**:
1. Check browser console for errors
2. Verify `VITE_API_URL` environment variable is set
3. Test backend URL directly: `https://your-backend-name.vercel.app/api/classrooms`
4. Check network tab in browser dev tools

---

## Quick Reference

### Environment Variables Needed:

**Frontend (Vercel)**:
```
VITE_API_URL=https://your-backend-name.vercel.app/api
```

**Backend (Vercel)**:
```
MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.wzlqllh.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
CORS_ORIGIN=https://your-frontend-name.vercel.app
```

### URLs After Deployment:

- **Backend API**: `https://your-backend-name.vercel.app`
- **Frontend**: `https://your-frontend-name.vercel.app`
- **API Endpoint**: `https://your-backend-name.vercel.app/api`

---

## Summary

1. ✅ Get backend URL from Vercel
2. ✅ Commit and push frontend changes
3. ✅ Deploy frontend on Vercel (Root Directory: `frontend`)
4. ✅ Set `VITE_API_URL` environment variable
5. ✅ Update backend `CORS_ORIGIN` with frontend URL
6. ✅ Test and verify everything works

**You're ready to deploy! Follow these steps and your frontend will be live!** 🚀
