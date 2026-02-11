"""Vision detection: YOLOv8 person count."""
import numpy as np

# Patch torch.load for PyTorch 2.6+ compatibility with Ultralytics checkpoints
# Official Ultralytics models are trusted, so weights_only=False is safe
import torch
_orig_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    """Patch torch.load to use weights_only=False for Ultralytics checkpoints."""
    kwargs.setdefault("weights_only", False)
    return _orig_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

# Lazy-load model on first use
_model = None

# COCO class index for "person"
PERSON_CLASS_ID = 0


def _get_model():
    """Load YOLOv8 model once (Ultralytics downloads on first run)."""
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO("yolov8n.pt")  # nano model for speed
    return _model


def count_persons(image: np.ndarray) -> int:
    """
    Run YOLOv8 on image and return number of persons detected.
    :param image: BGR numpy array (e.g. from cv2.imdecode)
    :return: Count of persons (class "person" in COCO)
    """
    if image is None or image.size == 0:
        return 0
    model = _get_model()
    results = model(image, verbose=False)
    count = 0
    for r in results:
        if r.boxes is None:
            continue
        for cls in r.boxes.cls:
            if int(cls) == PERSON_CLASS_ID:
                count += 1
    return count


def compute_motion_score(current_frame: np.ndarray, prev_frame: np.ndarray) -> float:
    """
    Compute motion intensity between two frames.
    :param current_frame: BGR numpy array (current frame)
    :param prev_frame: BGR numpy array (previous frame) or None
    :return: Motion score (0.0 to 1.0), higher = more motion
    """
    if prev_frame is None or current_frame is None:
        return 0.0
    
    if current_frame.shape != prev_frame.shape:
        return 0.0
    
    import cv2
    
    # Convert to grayscale
    gray_current = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    gray_prev = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    
    # Compute absolute difference
    diff = cv2.absdiff(gray_current, gray_prev)
    
    # Compute motion score: sum of pixel differences normalized by image size
    # Normalize to 0-1 range (max diff per pixel is 255)
    total_diff = np.sum(diff)
    max_possible_diff = diff.size * 255.0
    motion_score = min(total_diff / max_possible_diff, 1.0) if max_possible_diff > 0 else 0.0
    
    return motion_score
