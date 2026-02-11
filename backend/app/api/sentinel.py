"""Sentinel API: frame analysis (Empty Class detection)."""
import base64

import cv2
import numpy as np
from flask import Blueprint, request, jsonify

from app.sentinel.vision import count_persons, compute_motion_score
from app.sentinel.rules import process_empty_class_rule, process_mischief_rule, process_loud_noise_rule

bp = Blueprint("sentinel", __name__, url_prefix="/api/sentinel")


def _decode_frame(frame_b64: str) -> np.ndarray | None:
    """Decode base64 image string to BGR numpy array. Handles data URL prefix."""
    if not frame_b64:
        return None
    # Strip data URL prefix if present (e.g. data:image/jpeg;base64,...)
    if "," in frame_b64:
        frame_b64 = frame_b64.split(",", 1)[1]
    try:
        raw = base64.b64decode(frame_b64)
    except Exception:
        return None
    buf = np.frombuffer(raw, dtype=np.uint8)
    image = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    return image


@bp.route("/analyze-frame", methods=["POST", "OPTIONS"])
def analyze_frame():
    """
    POST /api/sentinel/analyze-frame
    Body: { "classroom_id": "8A", "frame": "data:image/jpeg;base64,..." }
    Runs YOLOv8 person count, applies empty-class rule (2 min empty → alert).
    Also computes motion and applies mischief rule (high motion → alert).
    """
    if request.method == "OPTIONS":
        from flask import Response
        from app.config import Config
        r = Response()
        r.headers["Access-Control-Allow-Origin"] = Config.CORS_ORIGIN
        r.headers["Access-Control-Allow-Headers"] = "Content-Type"
        r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return r

    data = request.get_json(silent=True) or {}
    classroom_id = data.get("classroom_id")
    frame_b64 = data.get("frame")

    if not classroom_id:
        return jsonify({"error": "classroom_id is required"}), 400
    if not frame_b64:
        return jsonify({"error": "frame is required (base64 image)"}), 400

    image = _decode_frame(frame_b64)
    if image is None:
        return jsonify({"error": "Invalid frame: could not decode base64 image"}), 400

    # Get previous frame from state for motion detection
    from app.sentinel.rules import _get_state, _get_lock
    lock = _get_lock(classroom_id)
    with lock:
        state = _get_state(classroom_id)
        prev_frame = state.get("prev_frame")

    # Compute person count and motion score
    person_count = count_persons(image)
    motion_score = compute_motion_score(image, prev_frame)

    # Apply rules
    empty_result = process_empty_class_rule(classroom_id, person_count)
    mischief_result = process_mischief_rule(classroom_id, motion_score, image)

    return jsonify({
        "classroom_id": classroom_id,
        "person_count": empty_result["person_count"],
        "motion_score": round(mischief_result["motion_score"], 3),
        "alert_created": empty_result["alert_created"] or mischief_result["alert_created"],
    })


@bp.route("/audio-level", methods=["POST", "OPTIONS"])
def audio_level():
    """
    POST /api/sentinel/audio-level
    Body: { "classroom_id": "8A", "level": 0.85 }
    Processes audio level and applies loud noise rule (high level for 5 consecutive requests → alert).
    """
    if request.method == "OPTIONS":
        from flask import Response
        from app.config import Config
        r = Response()
        r.headers["Access-Control-Allow-Origin"] = Config.CORS_ORIGIN
        r.headers["Access-Control-Allow-Headers"] = "Content-Type"
        r.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return r

    data = request.get_json(silent=True) or {}
    classroom_id = data.get("classroom_id")
    audio_level = data.get("level")

    if not classroom_id:
        return jsonify({"error": "classroom_id is required"}), 400
    if audio_level is None:
        return jsonify({"error": "level is required (0.0 to 1.0)"}), 400

    try:
        audio_level = float(audio_level)
        if not (0.0 <= audio_level <= 1.0):
            return jsonify({"error": "level must be between 0.0 and 1.0"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "level must be a number"}), 400

    result = process_loud_noise_rule(classroom_id, audio_level)

    return jsonify({
        "classroom_id": classroom_id,
        "audio_level": result["audio_level"],
        "alert_created": result["alert_created"],
    })
