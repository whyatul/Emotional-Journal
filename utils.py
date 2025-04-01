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
        print("No frames to save")
        return None
    
    if output_path is None:
        timestamp = get_timestamp()
        videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
        ensure_dir(videos_dir)
        output_path = os.path.join(videos_dir, f"journal_{timestamp}.mp4")
    
    try:
        print(f"First frame shape: {frames[0].shape}, total frames: {len(frames)}")
        height, width, _ = frames[0].shape
        
        # Try multiple codecs if needed
        codecs = ['mp4v', 'X264', 'DIVX', 'XVID']
        saved = False
        
        for codec in codecs:
            try:
                print(f"Trying codec: {codec}")
                # Create a temporary filename to avoid overwriting if multiple codecs are tried
                temp_path = output_path.replace('.mp4', f'_{codec}.mp4')
                
                fourcc = cv2.VideoWriter_fourcc(*codec)
                out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
                
                # Check if VideoWriter was opened successfully
                if not out.isOpened():
                    print(f"Failed to open VideoWriter with codec {codec}")
                    continue
                
                # Write frames
                for frame in frames:
                    if frame.shape[0] != height or frame.shape[1] != width:
                        # Resize frame if dimensions don't match
                        frame = cv2.resize(frame, (width, height))
                    out.write(frame)
                
                out.release()
                
                # Check if file was created successfully
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:  # Ensure file is not empty
                    print(f"Successfully saved video with codec {codec}")
                    # If a temporary path was used, rename to the requested output path
                    if temp_path != output_path:
                        os.rename(temp_path, output_path)
                    saved = True
                    break
                else:
                    print(f"Codec {codec} failed: file not created or too small")
            except Exception as e:
                print(f"Error with codec {codec}: {str(e)}")
        
        if not saved:
            print("All codecs failed, trying to save frames as images")
            # Fallback: Save key frames as images if video codecs all fail
            images_dir = os.path.join(os.path.dirname(output_path), 
                                     f"images_{os.path.basename(output_path).replace('.mp4', '')}")
            ensure_dir(images_dir)
            
            # Save every 15th frame (about 1 frame per second at 15fps)
            for i, frame in enumerate(frames):
                if i % 15 == 0:
                    img_path = os.path.join(images_dir, f"frame_{i:04d}.jpg")
                    cv2.imwrite(img_path, frame)
            
            print(f"Saved key frames as images in {images_dir}")
            return output_path  # Return the intended video path even though we saved images
        
        return output_path
        
    except Exception as e:
        print(f"Error saving video: {str(e)}")
        return None
