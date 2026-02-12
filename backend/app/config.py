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

    # Email / Dashboard config
    DASHBOARD_URL = os.getenv('DASHBOARD_URL', 'http://localhost:5173')
    TEACHER_EMAIL = os.getenv('TEACHER_EMAIL', 'teacher@school.com')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@school.com')
    PRINCIPAL_EMAIL = os.getenv('PRINCIPAL_EMAIL', 'principal@school.com')
    PARENT_EMAIL = os.getenv('PARENT_EMAIL', 'parent@school.com')

    # SMTP (real email delivery)
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM = os.getenv('SMTP_FROM')

    # Email assets
    SNAPSHOT_PLACEHOLDER_URL = os.getenv(
        'SNAPSHOT_PLACEHOLDER_URL',
        'https://placehold.co/640x360?text=Snapshot',
    )

    # Public backend base URL for links in emails
    BACKEND_PUBLIC_URL = os.getenv('BACKEND_PUBLIC_URL', 'http://localhost:5001')
