import cv2
import os
import datetime
import numpy as np
from pathlib import Path

def ensure_dir(directory):
    """Ensure that a directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_timestamp():
    """Get a formatted timestamp for filenames."""
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

def save_video(frames, fps=20, output_path=None):
    """Save frames as a video file."""
    if not frames:
        return None
    
    if output_path is None:
        timestamp = get_timestamp()
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
        ensure_dir(videos_dir)
        output_path = os.path.join(videos_dir, f"journal_{timestamp}.mp4")
    
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for frame in frames:
        out.write(frame)
    
    out.release()
    return output_path
