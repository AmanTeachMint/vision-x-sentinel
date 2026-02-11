"""Configuration for Vision X Sentinel backend."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration."""
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'http://localhost:5173')
    BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
    
    # MongoDB configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'vision_x_sentinel')
    
    # mock-media at repo root (parent of backend)
    MOCK_MEDIA_DIR = os.path.join(BACKEND_ROOT, '..', 'mock-media')
