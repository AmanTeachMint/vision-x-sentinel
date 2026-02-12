#!/bin/bash

# Vision X Sentinel Deployment Script
# This script helps deploy both frontend and backend

set -e

PROJECT_DIR="/home/aman_intern_teachmint_com/vision-x-sentinel"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "🚀 Vision X Sentinel Deployment Script"
echo "========================================"

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "📦 Installing PM2..."
    npm install -g pm2
fi

# Function to deploy backend
deploy_backend() {
    echo ""
    echo "🔧 Deploying Backend..."
    cd "$BACKEND_DIR"
    
    # Activate virtual environment if exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Check if backend is already running
    if pm2 list | grep -q "vision-backend"; then
        echo "⚠️  Backend already running. Restarting..."
        pm2 restart vision-backend
    else
        echo "▶️  Starting backend..."
        pm2 start run.py --name "vision-backend" --interpreter python3
    fi
    
    echo "✅ Backend deployed!"
    echo "   View logs: pm2 logs vision-backend"
}

# Function to deploy frontend
deploy_frontend() {
    echo ""
    echo "🎨 Deploying Frontend..."
    cd "$FRONTEND_DIR"
    
    # Check if we should build for production
    read -p "Build for production? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Building frontend..."
        npm run build
        
        # Check if serve is installed
        if ! command -v serve &> /dev/null; then
            echo "📦 Installing serve..."
            npm install -g serve
        fi
        
        # Stop existing frontend if running
        if pm2 list | grep -q "vision-frontend"; then
            pm2 delete vision-frontend
        fi
        
        echo "▶️  Starting frontend (production)..."
        pm2 start serve --name "vision-frontend" -- -s dist -l 5173
    else
        # Development mode
        if pm2 list | grep -q "vision-frontend"; then
            echo "⚠️  Frontend already running. Restarting..."
            pm2 restart vision-frontend
        else
            echo "▶️  Starting frontend (development)..."
            pm2 start npm --name "vision-frontend" -- run dev
        fi
    fi
    
    echo "✅ Frontend deployed!"
    echo "   View logs: pm2 logs vision-frontend"
}

# Function to show status
show_status() {
    echo ""
    echo "📊 Current Status:"
    pm2 list
    echo ""
    echo "📝 Recent Logs:"
    echo "   Backend:  pm2 logs vision-backend --lines 20"
    echo "   Frontend: pm2 logs vision-frontend --lines 20"
}

# Function to stop all
stop_all() {
    echo ""
    echo "🛑 Stopping all services..."
    pm2 stop vision-backend vision-frontend 2>/dev/null || true
    echo "✅ Services stopped"
}

# Main menu
echo ""
echo "Select deployment option:"
echo "1) Deploy Backend"
echo "2) Deploy Frontend"
echo "3) Deploy Both"
echo "4) Show Status"
echo "5) Stop All"
echo "6) Save PM2 Configuration"
read -p "Enter choice [1-6]: " choice

case $choice in
    1)
        deploy_backend
        ;;
    2)
        deploy_frontend
        ;;
    3)
        deploy_backend
        deploy_frontend
        ;;
    4)
        show_status
        ;;
    5)
        stop_all
        ;;
    6)
        echo "💾 Saving PM2 configuration..."
        pm2 save
        echo "✅ Configuration saved!"
        echo "   To start on boot, run: pm2 startup"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✨ Deployment complete!"
