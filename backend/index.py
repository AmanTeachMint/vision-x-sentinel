"""
Vercel entrypoint for Flask app.
Vercel automatically detects Flask apps when 'app' variable is exported.
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import create_app

# Create Flask app instance - Vercel will automatically detect this
app = create_app()
