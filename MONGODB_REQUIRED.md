# ⚠️ MongoDB Atlas Required

## Important Change

The application **now requires MongoDB Atlas** connection string to be set. It will **not** default to local MongoDB.

## Quick Setup

### 1. Get Your MongoDB Atlas Connection String

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Copy the connection string
5. Replace `<password>` with: `SV4BGryvvbfvAdNh`
6. Add database name: `/vision_x_sentinel`

**Your connection string should look like:**
```
mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
```

### 2. Set Environment Variable

#### For Local Development:

Create `backend/.env`:
```env
MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
```

#### For Vercel Deployment:

In Vercel Dashboard → Settings → Environment Variables:
```
MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
```

### 3. Whitelist IP Address

In MongoDB Atlas → Network Access:
- Click "Add IP Address"
- Click "Allow Access from Anywhere" (for demo)
- Or add specific IPs for production

## What Happens If MONGO_URI Is Not Set?

The application will **fail to start** with this error:

```
❌ Configuration Error: MONGO_URI environment variable is required.
Please set it to your MongoDB Atlas connection string.
```

## Why This Change?

- ✅ Forces explicit configuration (no accidental local MongoDB)
- ✅ Ensures production-ready setup from the start
- ✅ Prevents confusion between local and cloud databases
- ✅ Makes deployment easier (Atlas is required anyway)

## Still Want Local MongoDB?

If you really need local MongoDB for development, you can still use it by explicitly setting:

```env
MONGO_URI=mongodb://localhost:27017/
```

But you'll get a warning that Atlas is recommended.

---

**Bottom line:** Set `MONGO_URI` environment variable with your MongoDB Atlas connection string, and you're good to go! 🚀
