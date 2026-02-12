# Quick Start: Deploy Flask Backend on Vercel

## Step 1: Get MongoDB Atlas Connection String

You already have:
- Username: `amanmotghare_db_user`
- Password: `SV4BGryvvbfvAdNh`

### Get Your Connection String:

1. **Go to MongoDB Atlas**: [cloud.mongodb.com](https://cloud.mongodb.com)

2. **Click "Connect"** on your cluster

3. **Choose "Connect your application"**

4. **Copy the connection string** - It looks like:
   ```
   mongodb+srv://amanmotghare_db_user:<password>@cluster0.xxxxx.mongodb.net/
   ```

5. **Replace `<password>` with your password**:
   ```
   mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/
   ```

6. **Add database name at the end**:
   ```
   mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
   ```

**Save this connection string** - You'll need it for Vercel!

---

## Step 2: Verify IP Whitelist

1. **Go to MongoDB Atlas** → "Network Access"

2. **Add IP Address**:
   - Click "Add IP Address"
   - For demo: Click "Allow Access from Anywhere" (adds `0.0.0.0/0`)
   - Or add Vercel's IP ranges (optional, for production)

---

## Step 3: Deploy Backend on Vercel

### Option A: Via Vercel Dashboard (Easiest)

1. **Go to Vercel**: [vercel.com](https://vercel.com)
   - Sign up/Login with GitHub

2. **Import Project**:
   - Click "Add New Project"
   - Click "Import Git Repository"
   - Select your `vision-x-sentinel` repository
   - Click "Import"

3. **Configure Project**:
   - **Framework Preset**: Leave as "Other" or "Other"
   - **Root Directory**: Click "Edit" → Set to `backend`
   - **Build Command**: Leave empty (Vercel auto-detects Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (IMPORTANT!):
   Click "Environment Variables" and add these:

   ```
   Name: MONGO_URI
   Value: mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
   ```
   *(Replace `cluster0.xxxxx.mongodb.net` with your actual cluster URL)*

   ```
   Name: MONGO_DB_NAME
   Value: vision_x_sentinel
   ```

   ```
   Name: CORS_ORIGIN
   Value: https://your-frontend.vercel.app
   ```
   *(You'll update this after deploying frontend - for now use `*` or your local frontend URL)*

5. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (2-5 minutes)

6. **Get Your Backend URL**:
   - After deployment, Vercel shows: `https://your-backend-name.vercel.app`
   - **Save this URL** - You'll need it for frontend!

---

### Option B: Via Vercel CLI

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
# Paste: mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel

vercel env add MONGO_DB_NAME
# Paste: vision_x_sentinel

vercel env add CORS_ORIGIN
# Paste: * (or your frontend URL)

# Deploy to production
vercel --prod
```

---

## Step 4: Test Backend

After deployment, test your backend:

```bash
# Health check
curl https://your-backend-name.vercel.app/

# Should return:
# {"message": "Vision X Sentinel API is running", "status": "ok"}

# Test classrooms endpoint
curl https://your-backend-name.vercel.app/api/classrooms

# Should return: [] (empty array if database not seeded)
```

---

## Step 5: Seed Database

You need to seed the database with classrooms and videos.

### Option A: Run Seed Script Locally (Pointing to Atlas)

1. **Update local `.env` file**:
   ```bash
   cd backend
   nano .env
   ```

   Add:
   ```
   MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
   MONGO_DB_NAME=vision_x_sentinel
   ```

2. **Run seed script**:
   ```bash
   source venv/bin/activate
   python scripts/seed_db.py
   ```

3. **Verify**:
   ```bash
   curl https://your-backend-name.vercel.app/api/classrooms
   # Should return list of 20 classrooms
   ```

### Option B: Use MongoDB Compass (GUI Tool)

1. **Download**: [mongodb.com/products/compass](https://www.mongodb.com/products/compass)

2. **Connect** using your connection string

3. **Manually create collections** or import data

---

## Step 6: Verify Deployment

### Check Backend Logs:

1. Go to Vercel Dashboard
2. Click your project
3. Go to "Deployments" tab
4. Click latest deployment
5. Click "Functions" → View logs

### Test API Endpoints:

```bash
# Health check
curl https://your-backend-name.vercel.app/

# Get classrooms
curl https://your-backend-name.vercel.app/api/classrooms

# Get videos
curl https://your-backend-name.vercel.app/api/videos

# Get alerts
curl https://your-backend-name.vercel.app/api/alerts
```

---

## Troubleshooting

### Error: "MongoDB connection failed"

**Check:**
1. Connection string is correct (no extra spaces)
2. Password is correct (no special characters need encoding)
3. IP address is whitelisted in Atlas
4. Database name matches

**Fix:**
- Go to MongoDB Atlas → Network Access
- Add `0.0.0.0/0` to allow all IPs (for demo)

### Error: "Module not found"

**Check:**
- `requirements.txt` includes all dependencies
- Vercel is installing dependencies correctly

**Fix:**
- Check build logs in Vercel dashboard
- Verify `requirements.txt` is in `backend/` directory

### Error: "CORS error"

**Check:**
- `CORS_ORIGIN` environment variable is set
- Frontend URL matches exactly (including `https://`)

**Fix:**
- Update `CORS_ORIGIN` in Vercel environment variables
- Redeploy backend

### Cold Start Slow

**Normal behavior:**
- First request after inactivity takes 1-3 seconds
- Subsequent requests are fast (<500ms)

**This is expected** - Vercel serverless functions have cold starts.

---

## Next Steps

After backend is deployed:

1. ✅ **Get backend URL**: `https://your-backend-name.vercel.app`
2. ✅ **Deploy frontend** on Vercel (see `VERCEL_DEPLOYMENT.md`)
3. ✅ **Update CORS_ORIGIN** with frontend URL
4. ✅ **Test full application**

---

## Quick Checklist

- [ ] MongoDB Atlas cluster created
- [ ] Connection string obtained
- [ ] IP address whitelisted
- [ ] Backend code pushed to GitHub
- [ ] Backend deployed on Vercel
- [ ] Environment variables set (MONGO_URI, MONGO_DB_NAME, CORS_ORIGIN)
- [ ] Backend URL obtained
- [ ] Database seeded
- [ ] Backend tested and working

---

## Your Credentials Summary

**MongoDB Atlas:**
- Username: `amanmotghare_db_user`
- Password: `SV4BGryvvbfvAdNh`
- Connection String Format: `mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel`

**Vercel:**
- Backend URL: `https://your-backend-name.vercel.app` (get after deployment)

---

## Security Note

⚠️ **Important**: 
- Never commit passwords to Git
- Use environment variables (which you're doing ✅)
- Consider rotating passwords periodically
- For production, restrict IP whitelist to specific IPs

---

You're all set! Follow these steps and your Flask backend will be live on Vercel! 🚀
