"""Configuration for Vision X Sentinel backend."""
import os
from dotenv import load_dotenv

load_dotenv()

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
