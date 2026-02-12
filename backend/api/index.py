"""
Vercel serverless function entry point for Flask app.
Vercel Python runtime automatically detects Flask apps.
"""
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app

# Create Flask app instance - Vercel will automatically use this
app = create_app()
