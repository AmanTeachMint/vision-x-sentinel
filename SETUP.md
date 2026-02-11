# Vision X Sentinel - Setup Guide

This guide will help you set up the Vision X Sentinel project from scratch after cloning it from GitHub.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+ and npm** - [Download Node.js](https://nodejs.org/)
- **MongoDB** - [Download MongoDB](https://www.mongodb.com/try/download/community) (or use MongoDB Atlas cloud)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Verify Installations

```bash
# Check Python version
python3 --version  # Should be 3.10 or higher

# Check Node.js and npm
node --version
npm --version

# Check MongoDB (if installed locally)
mongod --version
```

## Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd vision-x-sentinel
```

## Step 2: Backend Setup

### 2.1 Navigate to Backend Directory

```bash
cd backend
```

### 2.2 Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt, indicating the virtual environment is active.

### 2.3 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** This may take a few minutes as it installs PyTorch and other large packages. If you encounter issues:

- **For CPU-only PyTorch (smaller download):**
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cpu
  pip install -r requirements.txt
  ```

- **For CUDA-enabled PyTorch (if you have NVIDIA GPU):**
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cu118
  pip install -r requirements.txt
  ```

### 2.4 Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp ../.env.example .env
   ```

2. Edit `.env` file (use any text editor):
   ```bash
   # On macOS/Linux
   nano .env
   
   # On Windows
   notepad .env
   ```

3. Update the values if needed:
   ```env
   FLASK_PORT=5000
   CORS_ORIGIN=http://localhost:5173
   MONGO_URI=mongodb://localhost:27017/
   MONGO_DB_NAME=vision_x_sentinel
   ```

   **For MongoDB Atlas (Cloud):**
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB_NAME=vision_x_sentinel
   ```

### 2.5 Start MongoDB

**If using local MongoDB:**

**On macOS (using Homebrew):**
```bash
brew services start mongodb-community
```

**On Linux:**
```bash
sudo systemctl start mongod
```

**On Windows:**
MongoDB should start automatically as a service. If not, start it from Services.

**If using MongoDB Atlas:**
- No local setup needed, just use your Atlas connection string in `.env`

### 2.6 Seed the Database

Run the seed script to populate the database with initial data:

```bash
python scripts/seed_db.py
```

You should see output like:
```
Seeded 8 videos (video1–video8). Videos should be in frontend/public/mock-media/
Seeded 8 classrooms (Class 1–8), each linked to a video.
Seeded 3 sample alerts (empty_class, mischief, loud_noise)
Seed complete. MongoDB database: vision_x_sentinel
```

### 2.7 Start the Backend Server

```bash
python run.py
```

The backend should start on `http://localhost:5000`. You should see:
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

**Keep this terminal window open** - the backend server needs to keep running.

## Step 3: Frontend Setup

Open a **new terminal window** (keep the backend running) and navigate to the frontend directory.

### 3.1 Navigate to Frontend Directory

```bash
cd vision-x-sentinel/frontend
```

### 3.2 Install Node Dependencies

```bash
npm install
```

This may take a few minutes as it downloads all React and other frontend dependencies.

### 3.3 Add Video Files (Required)

The application expects 8 video files in the `public/mock-media/` directory:

1. Create the directory if it doesn't exist:
   ```bash
   mkdir -p public/mock-media
   ```

2. Add your video files:
   - Place 8 video files named: `video1.mp4`, `video2.mp4`, `video3.mp4`, ..., `video8.mp4`
   - These videos will be displayed in the classroom cards
   - You can use any MP4 videos for testing

   **Example:**
   ```bash
   # Copy your videos to the directory
   cp /path/to/your/videos/*.mp4 public/mock-media/
   
   # Or rename existing videos
   mv your-video.mp4 public/mock-media/video1.mp4
   ```

### 3.4 Start the Frontend Development Server

```bash
npm run dev
```

The frontend should start on `http://localhost:5173`. You should see:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## Step 4: Access the Application

1. Open your web browser
2. Navigate to `http://localhost:5173`
3. You should see the Vision X Sentinel dashboard with 8 classroom cards
4. Videos should start playing automatically (if autoplay is enabled)

## Step 5: Verify Everything Works

1. **Check Backend API:**
   - Open `http://localhost:5000/` in your browser
   - You should see: `{"message": "Vision X Sentinel API is running", "status": "ok"}`

2. **Check Frontend:**
   - You should see 8 classroom cards
   - Videos should be playing (or ready to play)
   - Search bar, Logs, and Broadcast buttons should be visible

3. **Test Frame Capture:**
   - Open browser DevTools (F12)
   - Go to Network tab
   - You should see `POST /api/sentinel/analyze-frame` requests every 1.5 seconds when videos are playing

## Troubleshooting

### Backend Issues

**Problem: `ModuleNotFoundError` or `No module named 'app'`**
- Solution: Make sure you're in the `backend` directory and virtual environment is activated
- Run: `cd backend && source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)

**Problem: MongoDB connection error**
- Solution: 
  - Check if MongoDB is running: `mongosh` or `mongo` (older versions)
  - Verify `MONGO_URI` in `.env` file
  - For Atlas: Check your connection string and network access settings

**Problem: `torch` installation fails**
- Solution: Install PyTorch separately first:
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cpu
  pip install -r requirements.txt
  ```

**Problem: Port 5000 already in use**
- Solution: Change `FLASK_PORT` in `.env` to a different port (e.g., 5001)

### Frontend Issues

**Problem: `npm install` fails**
- Solution:
  - Clear npm cache: `npm cache clean --force`
  - Delete `node_modules` and `package-lock.json`
  - Run `npm install` again

**Problem: Videos not showing**
- Solution:
  - Verify videos exist in `frontend/public/mock-media/`
  - Check browser console for 404 errors
  - Ensure video files are named correctly (video1.mp4 through video8.mp4)

**Problem: CORS errors**
- Solution:
  - Verify `CORS_ORIGIN` in backend `.env` matches frontend URL (default: `http://localhost:5173`)
  - Restart backend server after changing `.env`

**Problem: Frame capture not working**
- Solution:
  - Check browser console for errors
  - Verify backend is running on correct port
  - Check Network tab for failed API requests
  - Ensure videos have `crossOrigin="anonymous"` attribute (should be automatic)

### General Issues

**Problem: YOLOv8 model download is slow**
- Solution: This is normal on first run. Ultralytics downloads the model (~6MB) automatically. It will be cached for future runs.

**Problem: "Autoplay blocked" messages**
- Solution: This is normal browser behavior. Click play manually on videos, or enable autoplay in browser settings.

## Project Structure Overview

```
vision-x-sentinel/
├── backend/
│   ├── app/              # Flask application
│   │   ├── api/          # API routes
│   │   ├── db/           # Database layer
│   │   ├── sentinel/     # AI detection logic
│   │   └── services/     # Utility services
│   ├── scripts/
│   │   └── seed_db.py   # Database seeding
│   ├── requirements.txt # Python dependencies
│   └── run.py           # Flask app entry point
├── frontend/
│   ├── src/
│   │   ├── api/         # API client
│   │   ├── components/  # React components
│   │   ├── hooks/       # Custom hooks
│   │   └── utils/       # Utilities
│   ├── public/
│   │   └── mock-media/  # Video files (add your videos here)
│   └── package.json     # Node dependencies
├── .env.example         # Environment variables template
├── README.md            # Project overview
└── SETUP.md             # This file
```

## Next Steps

After successful setup:

1. **Test Detection:**
   - Use videos showing empty rooms to test "Empty Class" detection
   - Use videos with high motion to test "Mischief" detection
   - Use videos with loud audio to test "Loud Noise" detection

2. **Explore Features:**
   - Click "Logs" to view alert history
   - Use search bar to filter classrooms
   - Click "Broadcast" to test broadcast functionality

3. **Development:**
   - Backend code is in `backend/app/`
   - Frontend code is in `frontend/src/`
   - Make changes and see them hot-reload automatically

## Getting Help

If you encounter issues not covered here:

1. Check the browser console (F12) for frontend errors
2. Check the backend terminal for server errors
3. Verify all prerequisites are installed correctly
4. Ensure MongoDB is running and accessible
5. Check that ports 5000 (backend) and 5173 (frontend) are not in use by other applications

## Quick Start Commands Summary

```bash
# Terminal 1 - Backend
cd vision-x-sentinel/backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
# Edit .env if needed
python scripts/seed_db.py
python run.py

# Terminal 2 - Frontend
cd vision-x-sentinel/frontend
npm install
# Add videos to public/mock-media/
npm run dev

# Open browser: http://localhost:5173
```

---

**Happy Coding! 🚀**
