#!/usr/bin/env python3
"""Seed MongoDB with 20 classrooms and videos from backend mock-media only.
- Discovers .mp4 files in backend mock-media (repo root).
- Clears frontend/public/mock-media and copies those videos there.
- Creates 20 classrooms (id "1".."20").
- Creates video documents with classroom_id (video 1 -> classroom 1, etc.).

Run from backend directory: python scripts/seed_db.py

Environment Variables Required:
- MONGO_URI: MongoDB connection string
  - Local: mongodb://localhost:27017/
  - Atlas: mongodb+srv://username:password@cluster.mongodb.net/vision_x_sentinel
- MONGO_DB_NAME: Database name (default: vision_x_sentinel)

Example for MongoDB Atlas:
  export MONGO_URI="mongodb+srv://amanmotghare_db_user:SV4BGryvvbfvAdNh@cluster0.xxxxx.mongodb.net/vision_x_sentinel"
  python scripts/seed_db.py
"""
import sys
import os
import shutil



# Add backend root to path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.store import upsert_classroom, insert_alert, upsert_video, upsert_admin_profile

NUM_CLASSROOMS = 20
BACKEND_MOCK_MEDIA = "mock-media"  # relative to repo root (parent of backend)
FRONTEND_MOCK_MEDIA = "frontend/public/mock-media"  # relative to repo root


def get_repo_root():
    """Repo root = parent of backend directory."""
    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.dirname(backend_root)


def sync_mock_media():
    """
    - Clear all .mp4 in frontend/public/mock-media.
    - Copy all .mp4 from backend mock-media (repo root) to frontend/public/mock-media.
    - Return list of (video_id, filename, url) for each copied video.
    """
    repo_root = get_repo_root()
    backend_dir = os.path.join(repo_root, BACKEND_MOCK_MEDIA)
    frontend_dir = os.path.join(repo_root, FRONTEND_MOCK_MEDIA)

    if not os.path.exists(backend_dir):
        print(f"Backend mock-media not found: {backend_dir}")
        return []

    # Discover videos in backend mock-media only
    discovered = []
    for filename in sorted(os.listdir(backend_dir)):
        if filename.endswith(".mp4"):
            video_id = filename.replace(".mp4", "")
            url = f"/mock-media/{filename}"
            discovered.append((video_id, filename, url))

    # Ensure frontend directory exists
    os.makedirs(frontend_dir, exist_ok=True)

    # Remove all .mp4 from frontend public mock-media
    for name in os.listdir(frontend_dir):
        if name.endswith(".mp4"):
            path = os.path.join(frontend_dir, name)
            try:
                os.remove(path)
            except Exception as e:
                print(f"Warning: could not remove {path}: {e}")

    # Copy backend mock-media videos to frontend
    for video_id, filename, url in discovered:
        src = os.path.join(backend_dir, filename)
        dst = os.path.join(frontend_dir, filename)
        try:
            shutil.copy2(src, dst)
        except Exception as e:
            print(f"Warning: could not copy {src} -> {dst}: {e}")

    print(f"Synced {len(discovered)} videos: backend mock-media -> frontend/public/mock-media")
    for video_id, filename, _ in discovered:
        print(f"  - {filename} (id: {video_id})")
    return discovered


def seed_classrooms():
    """Create 20 classrooms: id '1'..'20', name 'Class 1'..'Class 20'. No video_id."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for i in range(1, NUM_CLASSROOMS + 1):
        cid = str(i)
        name = f"Class {i}"
        upsert_classroom(cid, name=name, current_status="active", video_id=None, updated_at=now)
    print(f"Seeded {NUM_CLASSROOMS} classrooms (id 1..{NUM_CLASSROOMS})")


def seed_videos(discovered):
    """
    Create one video document per discovered file. Randomize assignment so
    classrooms aren't grouped by file name.
    """
    import random
    shuffled = list(discovered)
    random.shuffle(shuffled)
    for i, (video_id, filename, url) in enumerate(shuffled):
        classroom_id = str((i % NUM_CLASSROOMS) + 1)
        upsert_video(video_id, filename, url, classroom_id=classroom_id)
    print(f"Seeded {len(discovered)} videos with classroom_id (1..{NUM_CLASSROOMS})")


def seed_alerts():
    """Sample alerts for classrooms 1, 2, 3."""
    for cid, atype in [("1", "empty_class"), ("2", "mischief"), ("3", "loud_noise")]:
        insert_alert(cid, atype, metadata={})
    print("Seeded 3 sample alerts (empty_class, mischief, loud_noise)")


def main():
    """Main seeding function with connection validation."""
    from app.config import Config
    
    print("=" * 60)
    print("Vision X Sentinel - Database Seeding")
    print("=" * 60)
    print(f"MongoDB URI: {Config.MONGO_URI[:50]}..." if len(Config.MONGO_URI) > 50 else f"MongoDB URI: {Config.MONGO_URI}")
    print(f"Database: {Config.MONGO_DB_NAME}")
    print("=" * 60)
    
    # Test MongoDB connection
    try:
        from app.db.store import get_mongo_db
        db = get_mongo_db()
        print("✅ MongoDB connection successful!")
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nPlease check:")
        print("1. MONGO_URI environment variable is set correctly")
        print("2. MongoDB is running (if local) or IP is whitelisted (if Atlas)")
        print("3. Connection string format is correct")
        sys.exit(1)
    
    print("\nStarting seed process...")
    discovered = sync_mock_media()
    seed_classrooms()
    seed_videos(discovered)
    seed_alerts()
    upsert_admin_profile({
        "name": "Admin",
        "email": "abha.raut@teachmint.com",
        "avatar_initials": "AR",
    })
    print("Seeded admin profile (abha.raut@teachmint.com)")
    print("\nSeed complete. MongoDB database: vision_x_sentinel")
    print("Frontend public mock-media now contains only videos from backend mock-media.")


if __name__ == "__main__":
    main() 