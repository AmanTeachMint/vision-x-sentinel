"""MongoDB schema: table names and default document shapes."""

# Table names
TABLE_CLASSROOMS = "classrooms"
TABLE_ALERTS = "alerts"
TABLE_VIDEOS = "videos"

# Default document shapes (for reference / validation)


def default_classroom(classroom_id: str, name: str, video_id: str = None) -> dict:
    """Default classroom document shape."""
    from datetime import datetime
    return {
        "id": classroom_id,
        "name": name,
        "current_status": "active",
        "video_id": video_id,
        "updated_at": datetime.utcnow().isoformat() + "Z",
    }


def default_alert(classroom_id: str, alert_type: str, image_snapshot_path: str = None, metadata: dict = None) -> dict:
    """Default alert document shape."""
    from datetime import datetime
    import uuid
    return {
        "id": str(uuid.uuid4()),
        "classroom_id": classroom_id,
        "type": alert_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "image_snapshot_path": image_snapshot_path,
        "metadata": metadata or {},
    }


def default_video(video_id: str, filename: str, url: str, classroom_id: str = None) -> dict:
    """Default video document shape."""
    from datetime import datetime
    return {
        "id": video_id,
        "filename": filename,
        "url": url,  # Public URL (cloud storage or static file)
        "classroom_id": classroom_id,  # Which classroom this video is assigned to
        "created_at": datetime.utcnow().isoformat() + "Z",
    }


# Valid values for reference
CLASSROOM_STATUSES = ("active", "inactive", "empty", "mischief", "loud_noise")
ALERT_TYPES = ("empty_class", "mischief", "loud_noise")
