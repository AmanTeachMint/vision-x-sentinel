"""MongoDB store: get/insert classrooms, alerts, and videos."""
from pymongo import MongoClient
from app.config import Config
from app.db.schema import TABLE_CLASSROOMS, TABLE_ALERTS, TABLE_VIDEOS, default_classroom, default_alert, default_video

_client = None
_db = None


def get_mongo_db():
    """Get or create MongoDB database connection."""
    global _client, _db
    if _client is None:
        _client = MongoClient(Config.MONGO_URI)
        _db = _client[Config.MONGO_DB_NAME]
        # Ensure indexes for better performance
        _ensure_indexes()
    return _db


def _ensure_indexes():
    """Create indexes for better query performance."""
    db = get_mongo_db()
    db[TABLE_CLASSROOMS].create_index("id", unique=True)
    db[TABLE_ALERTS].create_index("classroom_id")
    db[TABLE_ALERTS].create_index("timestamp")
    db[TABLE_VIDEOS].create_index("id", unique=True)
    db[TABLE_VIDEOS].create_index("classroom_id")


def get_all_classrooms():
    """Return all classrooms."""
    db = get_mongo_db()
    collection = db[TABLE_CLASSROOMS]
    return list(collection.find({}, {"_id": 0}))


def get_classroom_by_id(classroom_id: str):
    """Return one classroom by id or None."""
    db = get_mongo_db()
    collection = db[TABLE_CLASSROOMS]
    result = collection.find_one({"id": classroom_id}, {"_id": 0})
    return result


def upsert_classroom(classroom_id: str, name: str = None, current_status: str = None,
                     video_id: str = None, updated_at: str = None):
    """Insert or update a classroom. Returns the document.
    Note: video_id references a video in the videos collection.
    """
    from datetime import datetime
    db = get_mongo_db()
    collection = db[TABLE_CLASSROOMS]
    existing = collection.find_one({"id": classroom_id})
    now = (updated_at or datetime.utcnow().isoformat() + "Z")
    doc = {
        "id": classroom_id,
        "name": name or (existing.get("name") if existing else f"Class {classroom_id}"),
        "current_status": current_status or (existing.get("current_status") if existing else "active"),
        "video_id": video_id if video_id is not None else (existing.get("video_id") if existing else None),
        "updated_at": now,
    }
    collection.replace_one({"id": classroom_id}, doc, upsert=True)
    return doc


def get_alerts(classroom_id: str = None, limit: int = None):
    """Return alerts, optionally filtered by classroom_id. Newest first."""
    db = get_mongo_db()
    collection = db[TABLE_ALERTS]
    query = {}
    if classroom_id:
        query["classroom_id"] = classroom_id
    cursor = collection.find(query, {"_id": 0}).sort("timestamp", -1)
    if limit is not None:
        cursor = cursor.limit(limit)
    return list(cursor)


def insert_alert(classroom_id: str, alert_type: str, image_snapshot_path: str = None, metadata: dict = None):
    """Insert an alert and return the document."""
    doc = default_alert(classroom_id, alert_type, image_snapshot_path, metadata)
    db = get_mongo_db()
    collection = db[TABLE_ALERTS]
    result = collection.insert_one(doc)
    # Remove MongoDB _id from returned doc to match TinyDB behavior
    doc.pop("_id", None)
    return doc


# Video functions
def get_all_videos(classroom_id: str = None):
    """Return all videos, optionally filtered by classroom_id."""
    db = get_mongo_db()
    collection = db[TABLE_VIDEOS]
    query = {}
    if classroom_id:
        query["classroom_id"] = classroom_id
    return list(collection.find(query, {"_id": 0}))


def get_video_by_id(video_id: str):
    """Return one video by id or None."""
    db = get_mongo_db()
    collection = db[TABLE_VIDEOS]
    result = collection.find_one({"id": video_id}, {"_id": 0})
    return result


def upsert_video(video_id: str, filename: str, url: str, classroom_id: str = None):
    """Insert or update a video. Returns the document."""
    doc = default_video(video_id, filename, url, classroom_id)
    db = get_mongo_db()
    collection = db[TABLE_VIDEOS]
    collection.replace_one({"id": video_id}, doc, upsert=True)
    return doc


def delete_video(video_id: str):
    """Delete a video by id. Returns True if deleted, False if not found."""
    db = get_mongo_db()
    collection = db[TABLE_VIDEOS]
    result = collection.delete_one({"id": video_id})
    return result.deleted_count > 0
