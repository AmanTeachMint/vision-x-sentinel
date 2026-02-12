# MongoDB Setup Guide

## Quick Setup for MongoDB Atlas (Cloud)

### Your Credentials
- **Username**: `amanmotghare_db_user`
- **Password**: `SV4BGryvvbfvAdNh`

### Step 1: Get Connection String

1. Go to [MongoDB Atlas](https://cloud.mongodb.com)
2. Click **"Connect"** on your cluster
3. Choose **"Connect your application"**
4. Copy the connection string
5. Replace `<password>` with: `SV4BGryvvbfvAdNh`
6. Add database name: `/vision_x_sentinel`

**Final connection string format:**
```
mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
```

### Step 2: Whitelist IP Address

1. Go to **"Network Access"** in MongoDB Atlas
2. Click **"Add IP Address"**
3. For demo: Click **"Allow Access from Anywhere"** (`0.0.0.0/0`)
4. For production: Add specific IPs

### Step 3: Set Environment Variable

#### For Local Development:

Create `backend/.env`:
```env
MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
```

#### For Vercel Deployment:

1. Go to Vercel Dashboard → Your Project
2. Go to **Settings** → **Environment Variables**
3. Add:
   ```
   MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
   MONGO_DB_NAME=vision_x_sentinel
   ```

### Step 4: Test Connection

```bash
cd backend
source venv/bin/activate
python scripts/seed_db.py
```

You should see:
```
✅ MongoDB connection successful!
✅ Seed complete!
```

---

## Local MongoDB (Alternative)

If you prefer local MongoDB for development:

### Install MongoDB Locally

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongod
```

### Set Environment Variable

Create `backend/.env`:
```env
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=vision_x_sentinel
```

---

## Connection String Formats

### MongoDB Atlas (Cloud)
```
mongodb+srv://username:password@cluster.mongodb.net/database
```

### Local MongoDB
```
mongodb://localhost:27017/
```

### MongoDB Atlas with Options
```
mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
```

---

## Troubleshooting

### Error: "MongoDB connection failed"

**Check:**
1. Connection string is correct (no extra spaces)
2. Password doesn't need URL encoding (unless it has special chars)
3. IP address is whitelisted in Atlas
4. Database name matches

**Fix:**
- Verify connection string format
- Check Network Access in Atlas
- Test connection string in MongoDB Compass

### Error: "ServerSelectionTimeoutError"

**Cause:** Can't reach MongoDB server

**Fix:**
- Check IP whitelist in Atlas
- Verify internet connection
- Check firewall settings

### Error: "Authentication failed"

**Cause:** Wrong username/password

**Fix:**
- Verify credentials in Atlas
- Check connection string has correct password
- Ensure username includes database user (not Atlas account)

---

## Security Best Practices

1. **Never commit passwords to Git**
   - Use `.env` files (already in `.gitignore`)
   - Use environment variables in Vercel

2. **Rotate passwords periodically**
   - Change database user password in Atlas
   - Update environment variables

3. **Restrict IP access**
   - For production, whitelist specific IPs
   - Don't use `0.0.0.0/0` in production

4. **Use connection string with database name**
   - Include database name in connection string
   - Prevents accidental access to wrong database

---

## Code Changes Made

The code now:
- ✅ Uses `MONGO_URI` environment variable (supports both local and Atlas)
- ✅ Validates connection on startup
- ✅ Shows clear error messages if connection fails
- ✅ Works with both `mongodb://` and `mongodb+srv://` formats
- ✅ Defaults to local MongoDB if `MONGO_URI` not set (with warning)

---

## Quick Reference

**Environment Variables:**
```env
MONGO_URI=mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
MONGO_DB_NAME=vision_x_sentinel
```

**Test Connection:**
```bash
python scripts/seed_db.py
```

**Check Connection in Code:**
```python
from app.db.store import get_mongo_db
db = get_mongo_db()  # Will connect and validate
```

---

Your MongoDB connection is now configured to use Atlas by default when `MONGO_URI` is set! 🚀
