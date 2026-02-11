# Vision X Sentinel

A classroom monitoring system that uses AI (YOLOv8) and audio analysis to detect empty classrooms, mischief, and loud noise in real-time.

## Tech Stack

- **Backend:** Flask, Python 3.10+, MongoDB, YOLOv8 (Ultralytics), OpenCV
- **Frontend:** React 18, Vite, Tailwind CSS
- **AI/ML:** YOLOv8 for person detection, OpenCV for motion detection

## Prerequisites

- Python 3.10 or higher
- Node.js 16+ and npm
- MongoDB (running locally or remote)
- 8 video files in `frontend/public/mock-media/` (video1.mp4 through video8.mp4)

## Quick Start

**For detailed setup instructions, see [SETUP.md](./SETUP.md)**

Quick setup commands:
```bash
# Backend
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
python scripts/seed_db.py
python run.py

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

## Installation

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd vision-x-sentinel/backend
   ```

2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file (copy from `.env.example` at repo root):
   ```bash
   cp ../.env.example .env
   # Edit .env with your MongoDB URI if needed
   ```

5. Seed the database:
   ```bash
   python scripts/seed_db.py
   ```

6. Run the backend server:
   ```bash
   python run.py
   ```
   Backend will run on `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd vision-x-sentinel/frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

## How It Works

### Automatic Detection

- **Frame Capture:** When videos play, the frontend automatically captures frames every 1.5 seconds and sends them to the backend for analysis.
- **Person Detection:** Backend uses YOLOv8 to count persons in each frame.
- **Empty Class Detection:** If no persons are detected for 2+ minutes, an "Empty Class" alert is created.
- **Motion Detection:** High motion between consecutive frames (sustained for 3+ frames) triggers a "Mischief" alert.
- **Audio Analysis:** Audio levels are captured every 1 second. Sustained high levels (5+ seconds) trigger a "Loud Noise" alert.

### Alert System

- Alerts appear as toast notifications in the frontend
- Alert logs can be viewed by clicking the "Logs" button
- All alerts are stored in MongoDB and can be queried via the API

## API Endpoints

- `GET /api/classrooms` - Get all classrooms
- `GET /api/classrooms/<id>` - Get a specific classroom
- `GET /api/alerts` - Get all alerts (optional `?classroom_id=<id>` filter)
- `GET /api/videos` - Get all videos
- `POST /api/sentinel/analyze-frame` - Analyze a frame (person count, motion, empty class detection)
- `POST /api/sentinel/audio-level` - Process audio level (loud noise detection)

## Project Structure

```
vision-x-sentinel/
├── backend/
│   ├── app/
│   │   ├── api/          # Flask API routes
│   │   ├── db/            # Database layer (MongoDB)
│   │   ├── sentinel/      # AI detection logic
│   │   └── services/      # Utility services
│   ├── scripts/
│   │   └── seed_db.py     # Database seeding script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/           # API client
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   └── utils/         # Utility functions
│   └── public/
│       └── mock-media/    # Video files
└── mock-media/            # Additional mock videos
```

## Notes

- YOLOv8 model (`yolov8n.pt`) will be automatically downloaded by Ultralytics on first run
- Videos should be placed in `frontend/public/mock-media/` directory
- MongoDB connection string can be configured in `.env` file
- Frame capture stops automatically if the backend server is down (after 3 consecutive failures) and resumes when the server comes back

## Development

- Backend runs in debug mode by default
- Frontend uses Vite HMR (Hot Module Replacement) for fast development
- CORS is enabled for `http://localhost:5173` by default
