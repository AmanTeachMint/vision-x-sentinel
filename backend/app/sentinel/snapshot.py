"""Save alert frames as snapshot images for evidence and email."""
import os
from datetime import datetime
from typing import Optional

from app.config import Config


def save_snapshot(frame, classroom_id: str, alert_type: str) -> Optional[str]:
    """
    Save a frame (BGR numpy array) to static/snapshots and return the filename.
    Filename is used in image_snapshot_path and served at GET /api/snapshots/<filename>.
    :param frame: numpy array (BGR from cv2) or None
    :param classroom_id: e.g. "8A"
    :param alert_type: e.g. "mischief", "empty_class", "loud_noise"
    :return: filename (e.g. "8A_mischief_2025-02-11T12-00-00.jpg") or None if frame invalid
    """
    if frame is None:
        return None
    try:
        import cv2
    except ImportError:
        return None

    snap_dir = Config.SNAPSHOTS_DIR
    os.makedirs(snap_dir, exist_ok=True)

    safe_id = "".join(c if c.isalnum() else "_" for c in classroom_id)
    safe_type = "".join(c if c.isalnum() else "_" for c in alert_type)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"{safe_id}_{safe_type}_{ts}.jpg"
    path = os.path.join(snap_dir, filename)
    if not cv2.imwrite(path, frame):
        return None
    return filename
