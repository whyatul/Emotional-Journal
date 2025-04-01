import streamlit as st
import cv2
import os
import time
import datetime
from utils import save_video, ensure_dir, get_timestamp

# Set up the app
st.set_page_config(page_title="Emotional Journal", page_icon="📝")

# Custom CSS to center content
st.markdown("""
<style>
    .block-container {
        max-width: 80%;
        margin: 0 auto;
        padding-top: 2rem;
    }
    .stButton button {
        display: block;
        margin: 0 auto;
    }
    .stTextInput, .stSelectbox, .stTextArea {
        text-align: center;
    }
    div.stMarkdown {
        text-align: center;
    }
    div.stTitle {
        text-align: center;
    }
    button {
        display: block;
        margin: 0 auto;
    }
    .css-1kyxreq etr89bj0 {
        display: flex;
        justify-content: center;
    }
    .stHeader h1 {
        text-align: center;
    }
    h1, h2, h3, h4, h5, h6 {
        text-align: center;
    }
    img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .stVideo > div {
        display: flex;
        justify-content: center;
    }
</style>
""", unsafe_allow_html=True)

# Ensure videos directory exists
videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
ensure_dir(videos_dir)

# App title and description
st.title("Emotional Journal")
st.write("Record your emotional state and journal your thoughts.")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Record New Entry", "View Past Entries"])

# Record New Entry page
if page == "Record New Entry":
    st.header("Record a New Journal Entry")
    
    # Text input for journal title (mandatory)
    journal_title = st.text_input("Entry Title (required)")
    if not journal_title:
        st.warning("Please enter a title for your journal entry.")
    
    # Emotional state selection
    emotion = st.selectbox(
        "How are you feeling?",
        ["Happy", "Sad", "Anxious", "Calm", "Angry", "Grateful", "Confused", "Other"]
    )
    
    # Text area for written journal
    journal_text = st.text_area("Write your thoughts (optional)", height=150)
    
    # Recording controls
    st.subheader("Video Recording")
    start_recording = st.button("Start Recording")
    
    if start_recording and journal_title:
        frames = []
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Error: Could not open webcam.")
        else:
            recording_placeholder = st.empty()
            stop_button_placeholder = st.empty()
            save_button_placeholder = st.empty()
            stop_recording = False
            save_recording = False
            
            while not stop_recording and not save_recording:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Convert BGR to RGB for display
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(frame)  # Store original frame for saving
                
                # Display the frame
                recording_placeholder.image(rgb_frame, channels="RGB")
                
                # Update stop and save buttons with unique keys
                stop_recording = stop_button_placeholder.button("Stop Recording", key=f"stop_recording_{time.time()}")
                save_recording = save_button_placeholder.button("Save", key=f"save_recording_{time.time()}")
                time.sleep(0.05)  # Small delay to prevent overwhelming the UI
            
            cap.release()
            
            if frames:
                # Save the video to the videos directory with the title as the filename
                video_filename = f"{journal_title.replace(' ', '_')}.mp4"
                video_path = os.path.join(videos_dir, video_filename)
                
                with st.spinner("Saving your journal entry..."):
                    saved_path = save_video(frames, output_path=video_path)
                
                if saved_path:
                    # Save metadata
                    metadata_file = os.path.join(videos_dir, f"{journal_title.replace(' ', '_')}.txt")
                    with open(metadata_file, "w") as f:
                        f.write(f"Title: {journal_title}\n")
                        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Emotion: {emotion}\n\n")
                        f.write(journal_text)
                    
                    st.success(f"Journal entry saved successfully!")
                    st.video(saved_path)
                else:
                    st.error("Failed to save the video.")
            else:
                st.warning("No frames were recorded.")
        recording_placeholder.empty()
        stop_button_placeholder.empty()
        save_button_placeholder.empty()
    elif start_recording and not journal_title:
        st.error("Please enter a title before starting the recording.")

# View Past Entries page
elif page == "View Past Entries":
    st.header("Past Journal Entries")
    
    # Get list of video files
    video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
    
    if not video_files:
        st.info("No journal entries found. Record your first entry!")
    else:
        video_files.sort(reverse=True)  # Show newest first
        
        for video_file in video_files:
            video_path = os.path.join(videos_dir, video_file)
            timestamp = video_file.replace("journal_", "").replace(".mp4", "")
            
            # Try to load metadata
            metadata_file = os.path.join(videos_dir, video_file.replace(".mp4", ".txt"))
            if os.path.exists(metadata_file):
                with open(metadata_file, "r") as f:
                    metadata = f.read()
                
                # Extract title and date if available
                title = "Untitled Entry"
                date = timestamp
                emotion = "Not specified"
                
                for line in metadata.split("\n"):
                    if line.startswith("Title:"):
                        title = line.replace("Title:", "").strip()
                    elif line.startswith("Date:"):
                        date = line.replace("Date:", "").strip()
                    elif line.startswith("Emotion:"):
                        emotion = line.replace("Emotion:", "").strip()
            else:
                # Fallback if no metadata
                title = "Journal Entry"
                date = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
                emotion = "Not specified"
            
            # Create an expander for each entry
            with st.expander(f"{title} - {date} - Feeling: {emotion}"):
                st.video(video_path)
                
                # Display metadata if available
                if os.path.exists(metadata_file):
                    with open(metadata_file, "r") as f:
                        content = f.read().split("\n\n", 1)
                        if len(content) > 1:
                            st.write(content[1])  # Display journal text
