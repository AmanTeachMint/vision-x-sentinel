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
    """Seed videos — URLs point to frontend/public/mock-media/ (served by Vite/Vercel).
    Automatically discovers all .mp4 files from mock-media directory."""
    # Get the mock-media directory path (repo root)
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mock_media_dir = os.path.join(backend_root, '..', 'mock-media')
    
    # Discover all .mp4 files in mock-media directory
    discovered_videos = []
    if os.path.exists(mock_media_dir):
        for filename in sorted(os.listdir(mock_media_dir)):
            if filename.endswith('.mp4'):
                # Use filename without extension as video_id
                video_id = filename.replace('.mp4', '')
                url = f"/mock-media/{filename}"
                discovered_videos.append((video_id, filename, url))
    
    # Also check frontend/public/mock-media for any additional videos
    frontend_mock_media = os.path.join(backend_root, '..', 'frontend', 'public', 'mock-media')
    if os.path.exists(frontend_mock_media):
        for filename in sorted(os.listdir(frontend_mock_media)):
            if filename.endswith('.mp4'):
                video_id = filename.replace('.mp4', '')
                url = f"/mock-media/{filename}"
                # Only add if not already discovered
                if not any(v[0] == video_id for v in discovered_videos):
                    discovered_videos.append((video_id, filename, url))
    
    # Seed all discovered videos
    for video_id, filename, url in discovered_videos:
        upsert_video(video_id, filename, url, None)  # classroom_id will be set when classrooms are created
    
    print(f"Seeded {len(discovered_videos)} videos from mock-media directories:")
    for video_id, filename, url in discovered_videos:
        print(f"  - {filename} (id: {video_id})")
    print("  Videos should be in frontend/public/mock-media/")
    
    return [v[0] for v in discovered_videos]  # Return list of video_ids


def seed_classrooms(video_ids):
    """Seed classrooms — creates a classroom for each video discovered."""
    now = datetime.utcnow().isoformat() + "Z"
    
    # Create classrooms for all videos
    classrooms = []
    used_ids = set()
    
    for idx, video_id in enumerate(video_ids, start=1):
        # Generate classroom name from video_id
        classroom_name = f"Class {video_id.replace('_', ' ').title()}"
        
        # Determine classroom_id: prefer video number if it's video1-8, otherwise use video_id or index
        if video_id.startswith('video') and len(video_id) > 5 and video_id[5:].isdigit():
            classroom_id = video_id[5:]  # Extract number from "video1" -> "1"
        elif video_id.isalnum() and len(video_id) <= 3:
            # Use video_id directly if it's short and alphanumeric
            classroom_id = video_id
        else:
            # Use index as fallback, but ensure uniqueness
            classroom_id = str(idx)
            counter = 1
            while classroom_id in used_ids:
                classroom_id = f"{idx}_{counter}"
                counter += 1
        
        # Ensure uniqueness
        if classroom_id in used_ids:
            classroom_id = f"{classroom_id}_{idx}"
        
        used_ids.add(classroom_id)
        classrooms.append((classroom_id, classroom_name, video_id))
    
    for cid, name, video_id in classrooms:
        upsert_classroom(cid, name=name, current_status="active", video_id=video_id, updated_at=now)
    
    print(f"\nSeeded {len(classrooms)} classrooms, each linked to a video:")
    for cid, name, video_id in classrooms:
        print(f"  - {name} (id: {cid}) -> {video_id}")


def seed_alerts():
    """Seed a few sample alerts (optional)."""
    now = datetime.utcnow()
    for i, (cid, atype) in enumerate([("1", "empty_class"), ("2", "mischief"), ("3", "loud_noise")]):
        # Use insert_alert from store.py (works with MongoDB)
        insert_alert(cid, atype, metadata={})
    print("Seeded 3 sample alerts (empty_class, mischief, loud_noise)")


def main():
    video_ids = seed_videos()
    seed_classrooms(video_ids)
    seed_alerts()
    print("\nSeed complete. MongoDB database:", "vision_x_sentinel")


if __name__ == "__main__":
    main()
