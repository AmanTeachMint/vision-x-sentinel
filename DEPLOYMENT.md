# Vision X Sentinel - Deployment Guide

This guide covers multiple deployment options for both frontend and backend.

## Table of Contents
1. [Quick Start (PM2 - Recommended)](#option-1-pm2-process-manager-recommended)
2. [Systemd Services](#option-2-systemd-services-linux-native)
3. [Docker Deployment](#option-3-docker-containers)
4. [Simple Deployment (Screen/Nohup)](#option-4-simple-deployment-screennohup)
5. [Production Setup with Nginx](#option-5-production-setup-with-nginx)

---

## Prerequisites

Before deploying, ensure:
- ✅ Backend dependencies installed (`pip install -r requirements.txt`)
- ✅ Frontend dependencies installed (`npm install`)
- ✅ MongoDB running and accessible
- ✅ Database seeded (`python scripts/seed_db.py`)
- ✅ Environment variables configured (`.env` file)

---

## Option 1: PM2 Process Manager (Recommended)

**Best for:** Easy deployment, auto-restart, process monitoring

### Install PM2
```bash
# Install PM2 globally
npm install -g pm2

# Or with sudo if needed
sudo npm install -g pm2
```

### Backend Deployment

1. **Create PM2 ecosystem file** (`ecosystem.config.js` in project root):
```bash
cd /home/aman_intern_teachmint_com/vision-x-sentinel
nano ecosystem.config.js
```

2. **Start backend with PM2:**
```bash
cd backend
pm2 start run.py --name "vision-backend" --interpreter python3 -- --host 0.0.0.0 --port 5000
```

Or create a startup script:
```bash
pm2 start "python3 run.py" --name "vision-backend" --cwd /home/aman_intern_teachmint_com/vision-x-sentinel/backend
```

### Frontend Deployment

**Option A: Development Mode (with hot reload)**
```bash
cd frontend
pm2 start npm --name "vision-frontend" -- run dev
```

**Option B: Production Build (recommended)**
```bash
# Build frontend
cd frontend
npm run build

# Serve with PM2 using a simple HTTP server
npm install -g serve
pm2 start serve --name "vision-frontend" -- -s dist -l 5173
```

### PM2 Commands
```bash
# View running processes
pm2 list

# View logs
pm2 logs vision-backend
pm2 logs vision-frontend

# Restart
pm2 restart vision-backend

# Stop
pm2 stop vision-backend

# Delete
pm2 delete vision-backend

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the instructions shown
```

---

## Option 2: Systemd Services (Linux Native)

**Best for:** Production servers, system-level service management

### Backend Service

1. **Create service file:**
```bash
sudo nano /etc/systemd/system/vision-backend.service
```

2. **Add this content:**
```ini
[Unit]
Description=Vision X Sentinel Backend
After=network.target mongod.service

[Service]
Type=simple
User=aman_intern_teachmint_com
WorkingDirectory=/home/aman_intern_teachmint_com/vision-x-sentinel/backend
Environment="PATH=/home/aman_intern_teachmint_com/vision-x-sentinel/backend/venv/bin"
ExecStart=/home/aman_intern_teachmint_com/vision-x-sentinel/backend/venv/bin/python run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable vision-backend
sudo systemctl start vision-backend

# Check status
sudo systemctl status vision-backend

# View logs
sudo journalctl -u vision-backend -f
```

### Frontend Service

1. **Create service file:**
```bash
sudo nano /etc/systemd/system/vision-frontend.service
```

2. **Add this content:**
```ini
[Unit]
Description=Vision X Sentinel Frontend
After=network.target

[Service]
Type=simple
User=aman_intern_teachmint_com
WorkingDirectory=/home/aman_intern_teachmint_com/vision-x-sentinel/frontend
ExecStart=/usr/bin/npm run dev
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable vision-frontend
sudo systemctl start vision-frontend

# Check status
sudo systemctl status vision-frontend
```

---

## Option 3: Docker Containers

**Best for:** Isolated environments, easy scaling, consistent deployments

### Create Dockerfile for Backend

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "run.py"]
```

### Create Dockerfile for Frontend

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source and build
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml` in project root:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_PORT=5000
      - MONGO_URI=mongodb://mongo:27017/
      - MONGO_DB_NAME=vision_x_sentinel
    depends_on:
      - mongo
    volumes:
      - ./mock-media:/app/mock-media

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend

  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

### Deploy with Docker
```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Option 4: Simple Deployment (Screen/Nohup)

**Best for:** Quick testing, temporary deployments

### Backend
```bash
cd backend
source venv/bin/activate

# Using screen
screen -S backend
python run.py
# Press Ctrl+A then D to detach

# Using nohup
nohup python run.py > backend.log 2>&1 &
```

### Frontend
```bash
cd frontend

# Using screen
screen -S frontend
npm run dev
# Press Ctrl+A then D to detach

# Using nohup
nohup npm run dev > frontend.log 2>&1 &
```

### Reattach to screens
```bash
screen -r backend
screen -r frontend
```

---

## Option 5: Production Setup with Nginx

**Best for:** Production deployments, reverse proxy, SSL

### Install Nginx
```bash
sudo apt-get update
sudo apt-get install nginx
```

### Nginx Configuration

Create `/etc/nginx/sites-available/vision-sentinel`:
```nginx
server {
    listen 80;
    server_name 10.201.0.108;  # Your VM IP or domain

    # Frontend (React app)
    location / {
        proxy_pass http://localhost:5173;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (videos)
    location /mock-media {
        alias /home/aman_intern_teachmint_com/vision-x-sentinel/frontend/public/mock-media;
    }
}
```

### Enable Site
```bash
sudo ln -s /etc/nginx/sites-available/vision-sentinel /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl reload nginx
```

---

## Environment Configuration

### Backend `.env` file
```env
FLASK_PORT=5000
CORS_ORIGIN=http://10.201.0.108:5173
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=vision_x_sentinel
```

### Frontend API Configuration

Update `frontend/src/api/client.js` to use environment variable:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://10.201.0.108:5000/api';
```

Create `frontend/.env.production`:
```env
VITE_API_URL=http://10.201.0.108:5000/api
```

---

## Quick Deployment Checklist

- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] MongoDB running
- [ ] Database seeded
- [ ] `.env` files configured
- [ ] Backend running and accessible
- [ ] Frontend built (if production)
- [ ] Frontend running and accessible
- [ ] Firewall ports open (5000, 5173)
- [ ] Services auto-start on boot (if needed)

---

## Troubleshooting

### Backend not starting
```bash
# Check logs
pm2 logs vision-backend
# OR
sudo journalctl -u vision-backend -f

# Check if port is in use
sudo lsof -i :5000
```

### Frontend not connecting to backend
- Check CORS_ORIGIN in backend `.env`
- Verify API_BASE_URL in frontend
- Check firewall rules

### MongoDB connection issues
```bash
# Check MongoDB status
sudo systemctl status mongod

# Check MongoDB logs
sudo tail -f /var/log/mongodb/mongod.log
```

---

## Recommended Setup

For your VM deployment, I recommend:
1. **PM2** for process management (easiest)
2. **Production build** for frontend (better performance)
3. **Nginx** as reverse proxy (optional, for production)

This gives you:
- ✅ Auto-restart on crashes
- ✅ Process monitoring
- ✅ Easy log viewing
- ✅ Simple start/stop commands
