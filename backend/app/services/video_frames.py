"""Video frame utilities for mock streams.
Note: In the current implementation, frames are captured directly in the frontend
(ClassCard.jsx) using canvas and sent to the backend via POST /api/sentinel/analyze-frame.
This module is kept for potential future use (e.g., server-side frame extraction from video files).
"""
import cv2
import numpy as np
from typing import Optional


def extract_frame_from_video(video_path: str, timestamp_seconds: float = 0.0) -> Optional[np.ndarray]:
    """
    Extract a single frame from a video file at a given timestamp.
    This is a utility function for server-side frame extraction if needed.
    
    :param video_path: Path to video file
    :param timestamp_seconds: Timestamp in seconds (default: 0.0 = first frame)
    :return: BGR numpy array (frame) or None if extraction fails
    """
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None
        
        # Seek to timestamp
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = int(timestamp_seconds * fps)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            return frame
        return None
    except Exception as e:
        print(f"Error extracting frame from {video_path}: {e}")
        return None


def get_frame_at_time(video_path: str, time_seconds: float) -> Optional[np.ndarray]:
    """Alias for extract_frame_from_video for backward compatibility."""
    return extract_frame_from_video(video_path, time_seconds)
