import cv2
import os
import argparse
from datetime import timedelta

# Function to format time as HH:MM:SS
def format_time(seconds):
    return str(timedelta(seconds=seconds)).split('.')[0]

# Parse command line arguments
parser = argparse.ArgumentParser(description='Extract frames from video at specific time intervals')
parser.add_argument('--video', type=str, default=r"/home/anonymus/emotional_journal/videos/y4uth4.mp4", 
                    help='Path to the video file')
parser.add_argument('--interval', type=float, default=1.0, 
                    help='Time interval between frames in seconds (default: 1.0)')
parser.add_argument('--start', type=float, default=0.0, 
                    help='Start time in seconds (default: 0.0)')
parser.add_argument('--end', type=float, default=-1, 
                    help='End time in seconds, -1 for full video (default: -1)')
parser.add_argument('--output', type=str, default='data', 
                    help='Output directory (default: data)')

args = parser.parse_args()

# Open the video file
video_path = args.video
vid = cv2.VideoCapture(video_path)

# Check if video opened successfully
if not vid.isOpened():
    print(f"Error: Could not open video file: {video_path}")
    exit()

# Get video properties
fps = vid.get(cv2.CAP_PROP_FPS)
total_frames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps if fps > 0 else 0

print(f"Video properties:")
print(f"FPS: {fps}")
print(f"Total frames: {total_frames}")
print(f"Duration: {format_time(duration)}")

# Determine frame interval based on time interval
frame_interval = int(fps * args.interval)
if frame_interval < 1:
    frame_interval = 1

# Determine start and end frames
start_frame = int(args.start * fps)
if args.end < 0:
    end_frame = total_frames
else:
    end_frame = int(args.end * fps)

# Create output directory if it doesn't exist
if not os.path.exists(args.output):
    os.makedirs(args.output)

print(f"Extracting frames every {args.interval} seconds (every {frame_interval} frames)")
print(f"Time range: {format_time(args.start)} to {format_time(args.end if args.end > 0 else duration)}")
print("Press 'q' to stop extraction")

# Set the video position to start frame
vid.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

current_frame = start_frame
frames_extracted = 0

while current_frame < end_frame:
    # Read the frame
    success, frame = vid.read()
    
    # Break if reached end of video
    if not success:
        print("End of video file reached")
        break
    
    # Get current timestamp in seconds
    current_time = current_frame / fps
    time_str = format_time(current_time)
    
    # Add timestamp to the frame
    cv2.putText(frame, f"Time: {time_str}", (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Display the frame
    cv2.imshow("Extracting Frames", frame)
    
    # Save only frames at specified intervals
    if (current_frame - start_frame) % frame_interval == 0:
        # Create filename with timestamp
        output_path = f"{args.output}/frame_{time_str.replace(':', '_')}.jpg"
        cv2.imwrite(output_path, frame)
        frames_extracted += 1
        
        # Print progress
        if frames_extracted % 10 == 0:
            print(f"Extracted {frames_extracted} frames ({time_str} / {format_time(duration)})")
    
    # Increment frame counter
    current_frame += 1
    
    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Extraction stopped by user")
        break

# Release resources
vid.release()
cv2.destroyAllWindows()

print(f"Successfully extracted {frames_extracted} frames to the '{args.output}' folder")
print(f"Time range: {format_time(args.start)} to {format_time(current_time)}")