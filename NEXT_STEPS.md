# Next Steps - Deploy Your Application

## ✅ Step 1: MongoDB Atlas Setup (DONE!)

Your MongoDB Atlas connection string:
```
mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.wzlqllh.mongodb.net/vision_x_sentinel
```

**Next:** Whitelist IP address in MongoDB Atlas

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Network Access"** (left sidebar)
3. Click **"Add IP Address"**
4. Click **"Allow Access from Anywhere"** (adds `0.0.0.0/0`)
   - This allows connections from anywhere (good for demo)
   - For production, add specific IPs only

---

## Step 2: Set Environment Variable Locally

### Create `backend/.env` file:

```bash
cd backend
cp ../.env.example .env
```

Or create `backend/.env` manually:
```env
FLASK_PORT=5000
CORS_ORIGIN=http://localhost:5173

MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.wzlqllh.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
```

---

## Step 3: Test Connection Locally

```bash
cd backend
source venv/bin/activate  # If using virtual environment

# Test MongoDB connection
python scripts/seed_db.py
```

You should see:
```
✅ MongoDB connection successful!
✅ Seed complete!
```

---

## Step 4: Deploy Backend on Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel**: [vercel.com](https://vercel.com)
   - Sign up/Login with GitHub

2. **Import Project**:
   - Click **"Add New Project"**
   - Click **"Import Git Repository"**
   - Select your `vision-x-sentinel` repository
   - Click **"Import"**

3. **Configure Project**:
   - **Root Directory**: Click **"Edit"** → Set to `backend`
   - **Framework Preset**: Leave as "Other"
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables**:
   Click **"Environment Variables"** and add:
   
   ```
   Name: MONGO_URI
   Value: mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.wzlqllh.mongodb.net/vision_x_sentinel
   ```
   
   ```
   Name: MONGO_DB_NAME
   Value: vision_x_sentinel
   ```
   
   ```
   Name: CORS_ORIGIN
   Value: *
   ```
   (You'll update this after deploying frontend)

5. **Deploy**:
   - Click **"Deploy"**
   - Wait 2-5 minutes for build

6. **Get Backend URL**:
   - After deployment: `https://your-backend-name.vercel.app`
   - **Save this URL!**

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Navigate to backend
cd backend

# Login
vercel login

# Deploy
vercel

# Set environment variables
vercel env add MONGO_URI
# Paste: mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.wzlqllh.mongodb.net/vision_x_sentinel

vercel env add MONGO_DB_NAME
# Paste: vision_x_sentinel

vercel env add CORS_ORIGIN
# Paste: *

# Deploy to production
vercel --prod
```

---

## Step 5: Seed Database (After Backend Deployed)

After backend is deployed, seed the database:

### Option A: Run Seed Script Locally (Pointing to Atlas)

```bash
cd backend
source venv/bin/activate

# Make sure .env file has MONGO_URI set
python scripts/seed_db.py
```

### Option B: Use MongoDB Compass

1. Download [MongoDB Compass](https://www.mongodb.com/products/compass)
2. Connect using your connection string
3. Manually create collections or import data

---

## Step 6: Test Backend

After deployment, test your backend:

```bash
# Health check
curl https://your-backend-name.vercel.app/

# Should return:
# {"message": "Vision X Sentinel API is running", "status": "ok"}

# Test classrooms endpoint
curl https://your-backend-name.vercel.app/api/classrooms

# Should return list of classrooms (after seeding)
```

---

## Step 7: Deploy Frontend on Vercel

1. **Go to Vercel Dashboard** → **"Add New Project"**

2. **Import Same Repository**:
   - Select your `vision-x-sentinel` repository
   - Click **"Import"**

3. **Configure Frontend**:
   - **Root Directory**: Set to `frontend`
   - **Framework Preset**: Vite (auto-detected)
   - **Build Command**: `npm run build` (auto-detected)
   - **Output Directory**: `dist` (auto-detected)

4. **Environment Variables**:
   Add:
   ```
   Name: VITE_API_URL
   Value: https://your-backend-name.vercel.app/api
   ```
   (Use your actual backend URL from Step 4)

5. **Deploy**: Click **"Deploy"**

6. **Get Frontend URL**: `https://your-frontend-name.vercel.app`

---

## Step 8: Update Backend CORS

After frontend deploys:

1. Go to Vercel Dashboard → Your Backend Project
2. Go to **Settings** → **Environment Variables**
3. Update `CORS_ORIGIN`:
   ```
   Value: https://your-frontend-name.vercel.app
   ```
4. Redeploy backend (or it auto-redeploys)

---

## Step 9: Update Frontend API Client

Edit `frontend/src/api/client.js`:

**Change line 2:**
```javascript
const API_BASE_URL = 'http://localhost:5000/api';
```

**To:**
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
```

Then commit and push - Vercel will auto-redeploy.

---

## Step 10: Verify Everything Works

1. **Open Frontend**: `https://your-frontend-name.vercel.app`
2. **Check Browser Console**: No errors
3. **Test Features**:
   - Classrooms load
   - Videos play
   - Frame analysis works
   - Alerts appear

---

## Quick Checklist

- [ ] MongoDB Atlas IP whitelisted (`0.0.0.0/0` for demo)
- [ ] Backend `.env` file created with `MONGO_URI`
- [ ] Local connection tested (`python scripts/seed_db.py`)
- [ ] Backend deployed on Vercel
- [ ] Backend environment variables set in Vercel
- [ ] Backend URL obtained
- [ ] Database seeded
- [ ] Backend tested (curl or browser)
- [ ] Frontend deployed on Vercel
- [ ] Frontend environment variable `VITE_API_URL` set
- [ ] Frontend API client updated
- [ ] Backend CORS updated with frontend URL
- [ ] Everything tested and working!

---

## Your URLs Summary

After deployment, you'll have:

- **Backend API**: `https://your-backend-name.vercel.app`
- **Frontend**: `https://your-frontend-name.vercel.app`
- **MongoDB Atlas**: `cluster0.wzlqllh.mongodb.net`

---

## Need Help?

- Check `VERCEL_DEPLOYMENT.md` for detailed instructions
- Check `MONGODB_SETUP.md` for MongoDB troubleshooting
- Check Vercel build logs if deployment fails

---

**You're ready to deploy! Start with Step 2 (create `.env` file) and work through the steps.** 🚀
