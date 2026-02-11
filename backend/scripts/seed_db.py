#!/usr/bin/env python3
"""Seed MongoDB with initial classrooms, videos, and sample alerts.
Run from backend directory: python scripts/seed_db.py
"""
import sys
import os

# Add backend root to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
from app.db.store import upsert_classroom, insert_alert, upsert_video


def seed_videos():
    """Seed 8 videos — URLs point to frontend/public/mock-media/ (served by Vite/Vercel)."""
    videos = [
        ("video1", "video1.mp4", "/mock-media/video1.mp4", "1"),
        ("video2", "video2.mp4", "/mock-media/video2.mp4", "2"),
        ("video3", "video3.mp4", "/mock-media/video3.mp4", "3"),
        ("video4", "video4.mp4", "/mock-media/video4.mp4", "4"),
        ("video5", "video5.mp4", "/mock-media/video5.mp4", "5"),
        ("video6", "video6.mp4", "/mock-media/video6.mp4", "6"),
        ("video7", "video7.mp4", "/mock-media/video7.mp4", "7"),
        ("video8", "video8.mp4", "/mock-media/video8.mp4", "8"),
    ]
    for vid, filename, url, classroom_id in videos:
        upsert_video(vid, filename, url, classroom_id)
    print("Seeded 8 videos (video1–video8). Videos should be in frontend/public/mock-media/")


def seed_classrooms():
    """Seed 8 classrooms — each references a video by video_id."""
    now = datetime.utcnow().isoformat() + "Z"
    classrooms = [
        ("1", "Class 1", "video1"),
        ("2", "Class 2", "video2"),
        ("3", "Class 3", "video3"),
        ("4", "Class 4", "video4"),
        ("5", "Class 5", "video5"),
        ("6", "Class 6", "video6"),
        ("7", "Class 7", "video7"),
        ("8", "Class 8", "video8"),
    ]
    for cid, name, video_id in classrooms:
        upsert_classroom(cid, name=name, current_status="active", video_id=video_id, updated_at=now)
    print("Seeded 8 classrooms (Class 1–8), each linked to a video.")


def seed_alerts():
    """Seed a few sample alerts (optional)."""
    now = datetime.utcnow()
    for i, (cid, atype) in enumerate([("1", "empty_class"), ("2", "mischief"), ("3", "loud_noise")]):
        # Use insert_alert from store.py (works with MongoDB)
        insert_alert(cid, atype, metadata={})
    print("Seeded 3 sample alerts (empty_class, mischief, loud_noise)")


def main():
    seed_videos()
    seed_classrooms()
    seed_alerts()
    print("Seed complete. MongoDB database:", "vision_x_sentinel")


if __name__ == "__main__":
    main()
