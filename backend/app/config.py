"""Configuration for Vision X Sentinel backend."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from backend directory so it works regardless of current working directory
_backend_root = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=_backend_root / ".env")

class Config:
    """Application configuration."""
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    CORS_ORIGIN = os.getenv('CORS_ORIGIN', 'http://localhost:5173')
    BACKEND_ROOT = os.path.dirname(os.path.dirname(__file__))
    
    # MongoDB configuration - MongoDB Atlas (Cloud) is required
    # Connection string format: mongodb+srv://username:password@cluster.mongodb.net/database
    # Example: mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'vision_x_sentinel')
    
    # Require MONGO_URI to be set (MongoDB Atlas is required)
    if not MONGO_URI:
        raise ValueError(
            "MONGO_URI environment variable is required. "
            "Please set it to your MongoDB Atlas connection string.\n"
            "Example: mongodb+srv://username:password@cluster.mongodb.net/vision_x_sentinel\n"
            "Get your connection string from: https://cloud.mongodb.com → Connect → Connect your application"
        )
    
    # Validate connection string format (should be Atlas format)
    if not MONGO_URI.startswith(('mongodb+srv://', 'mongodb://')):
        raise ValueError(
            f"Invalid MONGO_URI format: {MONGO_URI[:50]}...\n"
            "Expected format: mongodb+srv://username:password@cluster.mongodb.net/database"
        )
    
    # Warn if using local MongoDB (not recommended)
    if MONGO_URI.startswith('mongodb://localhost') or MONGO_URI.startswith('mongodb://127.0.0.1'):
        import warnings
        warnings.warn(
            "Using local MongoDB. For production/demo, use MongoDB Atlas (mongodb+srv://...).",
            UserWarning
        )
    
    # mock-media at repo root (parent of backend)
    MOCK_MEDIA_DIR = os.path.join(BACKEND_ROOT, '..', 'mock-media')

    # Snapshots directory (saved alert frames)
    SNAPSHOTS_DIR = os.path.join(BACKEND_ROOT, 'static', 'snapshots')

    # SMTP (optional – if set, intervention emails are sent to admin)
    SMTP_HOST = os.getenv('SMTP_HOST', '')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    SMTP_FROM = os.getenv('SMTP_FROM', 'visionx@school.org')
    # Admin email – receives alert notifications
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', '')
    # Optional base URL for links in emails (e.g. https://api.yourapp.com)
    BASE_URL = os.getenv('BASE_URL', '')
