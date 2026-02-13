"""Alert rules: time-based empty class detection and per-classroom state."""
import threading
import time

# Empty class: alert after this many seconds with zero persons
EMPTY_CLASS_DURATION_SEC = 20  # 2 minutes

# Mischief detection thresholds
MOTION_THRESHOLD = 0.18  # Motion score above this triggers increment
MISCHIEF_CONSECUTIVE_COUNT = 3  # Need this many consecutive high-motion frames
MISCHIEF_COOLDOWN_SEC = 60  # Don't alert again for this many seconds after an alert

# Loud noise detection thresholds
LOUD_NOISE_THRESHOLD = 0.1  # Audio level above this triggers increment
LOUD_NOISE_CONSECUTIVE_COUNT = 5  # Need this many consecutive high-level requests
LOUD_NOISE_COOLDOWN_SEC = 60  # Don't alert again for this many seconds after an alert

# Per-classroom state and lock
_state = {}  # classroom_id -> dict
_locks = {}  # classroom_id -> threading.Lock()


def _get_lock(classroom_id: str) -> threading.Lock:
    if classroom_id not in _locks:
        _locks[classroom_id] = threading.Lock()
    return _locks[classroom_id]


def _get_state(classroom_id: str) -> dict:
    """Get or create state for classroom. Caller must hold lock."""
    if classroom_id not in _state:
        _state[classroom_id] = {
            "first_empty_time": None,  # timestamp when we first saw 0 persons
            "prev_frame": None,  # for motion detection
            "consecutive_motion": 0,  # count of consecutive high-motion frames
            "last_mischief_alert_time": None,  # cooldown for mischief alerts
            "consecutive_high_audio": 0,  # count of consecutive high audio levels
            "last_loud_noise_alert_time": None,  # cooldown for loud noise alerts
        }
    return _state[classroom_id]


def on_alert_created(classroom_id: str, alert_type: str, current_frame, metadata: dict):
    """
    When any alert is triggered: save snapshot (if frame provided), insert alert with snapshot path,
    and send intervention email to admin.
    """
    from app.config import Config
    from app.db.store import get_classroom_by_id, insert_alert, upsert_classroom
    from app.sentinel.snapshot import save_snapshot
    from app.sentinel.email_service import send_email_to_admin

    snapshot_filename = save_snapshot(current_frame, classroom_id, alert_type)
    insert_alert(
        classroom_id,
        alert_type,
        image_snapshot_path=snapshot_filename,
        metadata=metadata,
    )
    classroom = get_classroom_by_id(classroom_id) or {}
    classroom_name = classroom.get("name") or classroom_id
    score = (
        metadata.get("motion_score")
        or metadata.get("audio_level")
        or metadata.get("empty_duration_sec")
        or 0
    )
    snapshot_url = ("/api/snapshots/" + snapshot_filename) if snapshot_filename else None
    if Config.BASE_URL and snapshot_url:
        snapshot_url = Config.BASE_URL.rstrip("/") + snapshot_url
    send_email_to_admin(
        classroom_name,
        score,
        alert_type,
        snapshot_url=snapshot_url,
        base_url=Config.BASE_URL or None,
    )


def process_empty_class_rule(classroom_id: str, person_count: int, current_frame=None) -> dict:
    """
    Apply empty-class rule: if 0 persons for >= 2 minutes, create alert and update classroom.
    Returns dict: { "alert_created": bool, "person_count": int }.
    """
    from app.db.store import upsert_classroom

    lock = _get_lock(classroom_id)
    with lock:
        state = _get_state(classroom_id)
        now = time.time()
        alert_created = False

        if person_count == 0:
            if state["first_empty_time"] is None:
                state["first_empty_time"] = now
            else:
                elapsed = now - state["first_empty_time"]
                if elapsed >= EMPTY_CLASS_DURATION_SEC:
                    on_alert_created(
                        classroom_id,
                        "empty_class",
                        current_frame,
                        metadata={"empty_duration_sec": round(elapsed)},
                    )
                    upsert_classroom(classroom_id, current_status="empty")
                    state["first_empty_time"] = None
                    alert_created = True
        else:
            state["first_empty_time"] = None

        return {"alert_created": alert_created, "person_count": person_count}


def process_mischief_rule(classroom_id: str, motion_score: float, current_frame) -> dict:
    """
    Apply mischief rule: if motion_score > threshold for consecutive frames, create alert.
    Returns dict: { "alert_created": bool, "motion_score": float }.
    """
    from app.db.store import upsert_classroom

    lock = _get_lock(classroom_id)
    with lock:
        state = _get_state(classroom_id)
        now = time.time()
        alert_created = False

        # Check cooldown
        if state["last_mischief_alert_time"] is not None:
            elapsed_since_alert = now - state["last_mischief_alert_time"]
            if elapsed_since_alert < MISCHIEF_COOLDOWN_SEC:
                # Still in cooldown, don't process
                state["prev_frame"] = current_frame.copy() if current_frame is not None else None
                return {"alert_created": False, "motion_score": motion_score}

        if motion_score > MOTION_THRESHOLD:
            state["consecutive_motion"] += 1
            if state["consecutive_motion"] >= MISCHIEF_CONSECUTIVE_COUNT:
                on_alert_created(
                    classroom_id,
                    "mischief",
                    current_frame,
                    metadata={"motion_score": round(motion_score, 3)},
                )
                upsert_classroom(classroom_id, current_status="mischief")
                state["consecutive_motion"] = 0
                state["last_mischief_alert_time"] = now
                alert_created = True
        else:
            state["consecutive_motion"] = 0

        # Update prev_frame for next comparison
        state["prev_frame"] = current_frame.copy() if current_frame is not None else None

        return {"alert_created": alert_created, "motion_score": motion_score}


def process_loud_noise_rule(classroom_id: str, audio_level: float) -> dict:
    """
    Apply loud noise rule: if audio_level > threshold for consecutive requests, create alert.
    Returns dict: { "alert_created": bool, "audio_level": float }.
    No snapshot for loud_noise (no frame); email still sent.
    """
    from app.db.store import upsert_classroom

    lock = _get_lock(classroom_id)
    with lock:
        state = _get_state(classroom_id)
        now = time.time()
        alert_created = False

        # Check cooldown
        if state["last_loud_noise_alert_time"] is not None:
            elapsed_since_alert = now - state["last_loud_noise_alert_time"]
            if elapsed_since_alert < LOUD_NOISE_COOLDOWN_SEC:
                # Still in cooldown, don't process
                return {"alert_created": False, "audio_level": audio_level}

        if audio_level > LOUD_NOISE_THRESHOLD:
            state["consecutive_high_audio"] += 1
            if state["consecutive_high_audio"] >= LOUD_NOISE_CONSECUTIVE_COUNT:
                on_alert_created(
                    classroom_id,
                    "loud_noise",
                    None,  # no frame for audio-only alert
                    metadata={"audio_level": round(audio_level, 3)},
                )
                upsert_classroom(classroom_id, current_status="loud_noise")
                state["consecutive_high_audio"] = 0
                state["last_loud_noise_alert_time"] = now
                alert_created = True
        else:
            state["consecutive_high_audio"] = 0

        return {"alert_created": alert_created, "audio_level": audio_level}
