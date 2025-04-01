import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import cv2
import os
import threading
import time
import datetime
import sys
import PIL.Image, PIL.ImageTk
from utils import save_video, ensure_dir, get_timestamp

# Ensure videos directory exists
videos_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "videos")
ensure_dir(videos_dir)

class EmotionalJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotional Journal")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.root.configure(bg="#f0f0f0")
        
        # Create frames for each "screen"
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.record_frame = tk.Frame(root, bg="#f0f0f0")
        self.history_frame = tk.Frame(root, bg="#f0f0f0")
        self.playback_frame = tk.Frame(root, bg="#f0f0f0")
        
        # Variables for recording
        self.recording = False
        self.frames = []
        self.cap = None
        self.video_path = None
        
        # Initialize all screens
        self.setup_main_screen()
        self.setup_record_screen()
        self.setup_history_screen()
        self.setup_playback_screen()
        
        # Show main screen initially
        self.show_main_screen()
    
    # Navigation functions
    def show_main_screen(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.record_frame.pack_forget()
        self.history_frame.pack_forget()
        self.playback_frame.pack_forget()
    
    def show_record_screen(self):
        self.record_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_forget()
        self.history_frame.pack_forget()
        self.playback_frame.pack_forget()
        
        # Reset form when showing this screen
        self.title_entry.delete(0, tk.END)
        self.emotion_var.set("Happy")
        self.journal_text.delete("1.0", tk.END)
        self.frames = []
        self.preview_label.config(image="")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
    
    def show_history_screen(self):
        self.load_journal_entries()  # Refresh entries
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_forget()
        self.record_frame.pack_forget()
        self.playback_frame.pack_forget()
    
    def show_playback_screen(self, video_path=None):
        if video_path and os.path.exists(video_path):
            self.video_path = video_path
            # Display the video title
            title = os.path.basename(video_path).replace(".mp4", "").replace("_", " ")
            self.playback_title.config(text=f"Playing: {title}")
            
            # For simplicity, we'll open the video in the default video player
            # as embedding video playback in Tkinter is complex
            if sys.platform == "win32":
                os.startfile(video_path)
            else:
                import subprocess
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, video_path])
        
        self.playback_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.pack_forget()
        self.record_frame.pack_forget()
        self.history_frame.pack_forget()
    
    # Setup functions for each screen
    def setup_main_screen(self):
        # Title and description
        title_label = tk.Label(
            self.main_frame, 
            text="Emotional Journal",
            font=("Helvetica", 24, "bold"),
            bg="#f0f0f0",
            pady=20
        )
        title_label.pack()
        
        description = tk.Label(
            self.main_frame,
            text="Record your emotional state and journal your thoughts.",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            pady=10
        )
        description.pack()
        
        # Buttons
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0", pady=20)
        button_frame.pack()
        
        record_button = tk.Button(
            button_frame,
            text="Record New Entry",
            font=("Helvetica", 12),
            command=self.show_record_screen,
            width=20,
            height=2,
            bg="#4CAF50",
            fg="white"
        )
        record_button.pack(pady=10)
        
        view_button = tk.Button(
            button_frame,
            text="View Past Entries",
            font=("Helvetica", 12),
            command=self.show_history_screen,
            width=20,
            height=2,
            bg="#2196F3",
            fg="white"
        )
        view_button.pack(pady=10)
    
    def setup_record_screen(self):
        # Title
        title_label = tk.Label(
            self.record_frame, 
            text="Record a New Journal Entry",
            font=("Helvetica", 18, "bold"),
            bg="#f0f0f0",
            pady=10
        )
        title_label.pack()
        
        # Form
        form_frame = tk.Frame(self.record_frame, bg="#f0f0f0", padx=20)
        form_frame.pack(fill=tk.X)
        
        # Title input
        title_frame = tk.Frame(form_frame, bg="#f0f0f0")
        title_frame.pack(fill=tk.X, pady=5)
        
        title_label = tk.Label(
            title_frame, 
            text="Entry Title (required):",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            width=20,
            anchor="w"
        )
        title_label.pack(side=tk.LEFT)
        
        self.title_entry = tk.Entry(title_frame, font=("Helvetica", 10), width=40)
        self.title_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Emotion selection
        emotion_frame = tk.Frame(form_frame, bg="#f0f0f0")
        emotion_frame.pack(fill=tk.X, pady=5)
        
        emotion_label = tk.Label(
            emotion_frame, 
            text="How are you feeling?",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            width=20,
            anchor="w"
        )
        emotion_label.pack(side=tk.LEFT)
        
        self.emotion_var = tk.StringVar(value="Happy")
        emotions = ["Happy", "Sad", "Anxious", "Calm", "Angry", "Grateful", "Confused", "Other"]
        emotion_menu = ttk.Combobox(
            emotion_frame, 
            textvariable=self.emotion_var,
            values=emotions,
            font=("Helvetica", 10),
            width=38
        )
        emotion_menu.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Journal text
        journal_label = tk.Label(
            form_frame, 
            text="Write your thoughts (optional):",
            font=("Helvetica", 10),
            bg="#f0f0f0",
            anchor="w"
        )
        journal_label.pack(anchor="w", pady=(10, 5))
        
        self.journal_text = scrolledtext.ScrolledText(
            form_frame, 
            font=("Helvetica", 10),
            height=5
        )
        self.journal_text.pack(fill=tk.X, pady=(0, 10))
        
        # Preview
        preview_label = tk.Label(
            self.record_frame,
            text="Camera Preview",
            font=("Helvetica", 12),
            bg="#f0f0f0"
        )
        preview_label.pack(pady=(10, 5))
        
        self.preview_label = tk.Label(self.record_frame, bg="black", height=15)
        self.preview_label.pack(fill=tk.X, padx=20)
        
        # Controls
        controls_frame = tk.Frame(self.record_frame, bg="#f0f0f0", pady=10)
        controls_frame.pack()
        
        self.start_button = tk.Button(
            controls_frame,
            text="Start Recording",
            font=("Helvetica", 10),
            command=self.toggle_recording,
            bg="#F44336",
            fg="white",
            width=15
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        self.stop_button = tk.Button(
            controls_frame,
            text="Stop Recording",
            font=("Helvetica", 10),
            command=self.stop_recording,
            state=tk.DISABLED,
            width=15
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        self.save_button = tk.Button(
            controls_frame,
            text="Save",
            font=("Helvetica", 10),
            command=self.save_recording,
            state=tk.DISABLED,
            bg="#4CAF50",
            fg="white",
            width=15
        )
        self.save_button.grid(row=0, column=2, padx=5)
        
        # Back button
        back_frame = tk.Frame(self.record_frame, bg="#f0f0f0", pady=10)
        back_frame.pack()
        
        back_button = tk.Button(
            back_frame,
            text="Back to Main",
            font=("Helvetica", 10),
            command=self.show_main_screen,
            width=15
        )
        back_button.pack()
    
    def setup_history_screen(self):
        # Title
        title_label = tk.Label(
            self.history_frame, 
            text="Journal History",
            font=("Helvetica", 18, "bold"),
            bg="#f0f0f0",
            pady=10
        )
        title_label.pack()
        
        # Scrollable canvas for entries
        canvas_frame = tk.Frame(self.history_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f0f0f0")
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Back button
        back_frame = tk.Frame(self.history_frame, bg="#f0f0f0", pady=10)
        back_frame.pack()
        
        back_button = tk.Button(
            back_frame,
            text="Back to Main",
            font=("Helvetica", 10),
            command=self.show_main_screen,
            width=15
        )
        back_button.pack()
    
    def setup_playback_screen(self):
        # Title
        self.playback_title = tk.Label(
            self.playback_frame, 
            text="Playing Journal Entry",
            font=("Helvetica", 18, "bold"),
            bg="#f0f0f0",
            pady=10
        )
        self.playback_title.pack()
        
        # Message
        message = tk.Label(
            self.playback_frame,
            text="Video is playing in your default video player.",
            font=("Helvetica", 12),
            bg="#f0f0f0",
            pady=20
        )
        message.pack()
        
        # Back button
        back_frame = tk.Frame(self.playback_frame, bg="#f0f0f0", pady=10)
        back_frame.pack()
        
        back_button = tk.Button(
            back_frame,
            text="Back to History",
            font=("Helvetica", 10),
            command=self.show_history_screen,
            width=15
        )
        back_button.pack()
    
    # Recording functions
    def toggle_recording(self):
        if not self.title_entry.get():
            messagebox.showerror("Error", "Please enter a title for your journal entry.")
            return
        
        if not self.recording:
            self.recording = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            
            # Setup camera with error handling
            try:
                # Try different camera indices if the default one fails
                camera_found = False
                for camera_index in range(3):  # Try indices 0, 1, 2
                    print(f"Trying camera index {camera_index}")
                    self.cap = cv2.VideoCapture(camera_index)
                    if self.cap.isOpened():
                        camera_found = True
                        break
                    self.cap.release()
                
                if not camera_found:
                    raise Exception("Could not find a working camera")
                    
            except Exception as e:
                messagebox.showerror("Camera Error", f"{str(e)}\nMake sure your webcam is connected and not in use by another application.")
                self.stop_recording()
                return
                
            # Start capture thread
            self.frames = []
            self.capture_thread = threading.Thread(target=self.capture_frames)
            self.capture_thread.daemon = True
            self.capture_thread.start()
            
            # Start updating preview
            self.update_preview()
    
    def capture_frames(self):
        """Capture frames from webcam and store them."""
        frame_count = 0
        while self.recording and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # Make a deep copy of the frame to ensure it's properly stored
                self.frames.append(frame.copy())
                frame_count += 1
                if frame_count % 30 == 0:  # Log every ~1 second at 30fps
                    print(f"Captured {frame_count} frames")
            else:
                print("Failed to capture frame")
                time.sleep(0.1)  # Avoid tight loop if camera is having issues
            time.sleep(0.03)  # Limit to ~30fps
        
        print(f"Capture thread ended with {len(self.frames)} frames collected")
    
    def update_preview(self):
        """Update the preview image in the UI."""
        if self.recording and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Convert to format Tkinter can display
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = PIL.Image.fromarray(frame)
                    
                    # Resize to fit the window
                    width = min(self.preview_label.winfo_width(), 640)
                    # Handle the initial case where width might be 1
                    if width < 10:  # Use default size if widget not properly sized yet
                        width = 640
                        height = 480
                    else:
                        ratio = width / frame.shape[1]
                        height = int(frame.shape[0] * ratio)
                        
                    img = img.resize((width, height), PIL.Image.LANCZOS)
                    
                    # Keep a reference to avoid garbage collection
                    self.photo = PIL.ImageTk.PhotoImage(image=img)
                    self.preview_label.config(image=self.photo)
                    
                    # Schedule the next update
                    self.root.after(30, self.update_preview)
                    return
            except Exception as e:
                print(f"Camera preview error: {str(e)}")
        
        # If we get here, there was a problem
        print("Stopping recording due to preview issue")
        self.stop_recording()
    
    def stop_recording(self):
        self.recording = False
        
        if self.cap:
            self.cap.release()
            self.cap = None
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def save_recording(self):
        """Save recorded frames to a video file."""
        self.stop_recording()
        
        if not self.frames:
            messagebox.showerror("Error", "No frames were recorded.")
            return
        
        print(f"Attempting to save {len(self.frames)} frames as video")
        
        # Save the video with the title as the filename
        video_filename = f"{self.title_entry.get().replace(' ', '_')}.mp4"
        video_path = os.path.join(videos_dir, video_filename)
        
        # Show saving progress
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Saving...")
        progress_window.geometry("300x100")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = tk.Label(
            progress_window,
            text=f"Saving your journal entry...\n({len(self.frames)} frames)",
            font=("Helvetica", 12),
            pady=20
        )
        progress_label.pack()
        
        # Start saving in a background thread
        def save_in_background():
            try:
                # Save video and metadata
                saved_path = save_video(self.frames, output_path=video_path)
                
                if saved_path and os.path.exists(saved_path):
                    print(f"Video saved successfully to {saved_path}")
                    # Save metadata
                    metadata_file = os.path.join(videos_dir, f"{self.title_entry.get().replace(' ', '_')}.txt")
                    with open(metadata_file, "w") as f:
                        f.write(f"Title: {self.title_entry.get()}\n")
                        f.write(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"Emotion: {self.emotion_var.get()}\n\n")
                        f.write(self.journal_text.get("1.0", tk.END))
                    
                    # Update UI on the main thread
                    self.root.after(0, lambda: self.save_complete(progress_window, saved_path))
                else:
                    print("Failed to save video: path not returned or file not created")
                    # Update UI on the main thread
                    self.root.after(0, lambda: self.save_failed(progress_window))
            except Exception as e:
                print(f"Error saving video: {str(e)}")
                self.root.after(0, lambda: self.save_failed(progress_window, str(e)))
        
        threading.Thread(target=save_in_background, daemon=True).start()
    
    def save_complete(self, progress_window, saved_path):
        """Handle successful video save."""
        progress_window.destroy()
        messagebox.showinfo("Success", f"Journal entry saved successfully!\nPath: {saved_path}")
        self.show_playback_screen(saved_path)
    
    def save_failed(self, progress_window, error_msg=""):
        """Handle failed video save."""
        progress_window.destroy()
        if error_msg:
            messagebox.showerror("Error", f"Failed to save the video.\nReason: {error_msg}")
        else:
            messagebox.showerror("Error", "Failed to save the video.")
    
    # Journal history functions
    def load_journal_entries(self):
        # Clear existing entries
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get list of video files
        video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
        
        if not video_files:
            no_entries = tk.Label(
                self.scrollable_frame,
                text="No journal entries found. Record your first entry!",
                font=("Helvetica", 12),
                bg="#f0f0f0",
                pady=20
            )
            no_entries.pack()
            return
        
        # Sort files by date (newest first)
        video_files.sort(reverse=True)
        
        # Display entries
        for video_file in video_files:
            self.add_entry_widget(video_file)
    
    def add_entry_widget(self, video_file):
        video_path = os.path.join(videos_dir, video_file)
        file_base = video_file.replace(".mp4", "")
        
        # Try to load metadata
        metadata_file = os.path.join(videos_dir, f"{file_base}.txt")
        if os.path.exists(metadata_file):
            with open(metadata_file, "r") as f:
                metadata = f.read()
            
            # Extract title and date if available
            title = "Untitled Entry"
            date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            emotion = "Not specified"
            journal_content = ""
            
            for line in metadata.split("\n"):
                if line.startswith("Title:"):
                    title = line.replace("Title:", "").strip()
                elif line.startswith("Date:"):
                    date = line.replace("Date:", "").strip()
                elif line.startswith("Emotion:"):
                    emotion = line.replace("Emotion:", "").strip()
            
            # Get journal content
            parts = metadata.split("\n\n", 1)
            if len(parts) > 1:
                journal_content = parts[1]
        else:
            # Fallback if no metadata
            title = file_base
            date = "Unknown date"
            emotion = "Not specified"
            journal_content = ""
        
        # Create entry widget
        entry_frame = tk.Frame(self.scrollable_frame, bg="#f5f5f5", 
                              bd=1, relief=tk.SOLID, padx=10, pady=10)
        entry_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Header
        title_label = tk.Label(
            entry_frame, 
            text=title,
            font=("Helvetica", 14, "bold"),
            bg="#f5f5f5",
            anchor="w"
        )
        title_label.pack(fill=tk.X)
        
        date_label = tk.Label(
            entry_frame, 
            text=date,
            font=("Helvetica", 10, "italic"),
            fg="#666666",
            bg="#f5f5f5",
            anchor="w"
        )
        date_label.pack(fill=tk.X)
        
        emotion_label = tk.Label(
            entry_frame, 
            text=f"Feeling: {emotion}",
            font=("Helvetica", 10),
            bg="#e6f3ff",
            fg="#333333",
            bd=1,
            relief=tk.SOLID,
            padx=5,
            pady=2,
            anchor="w"
        )
        emotion_label.pack(anchor="w", pady=(5, 10))
        
        # Content preview (if available)
        if journal_content:
            # Limit to 100 chars
            preview = journal_content[:100] + ("..." if len(journal_content) > 100 else "")
            content_label = tk.Label(
                entry_frame, 
                text=preview,
                font=("Helvetica", 10),
                bg="#f5f5f5",
                anchor="w",
                justify=tk.LEFT,
                wraplength=500
            )
            content_label.pack(fill=tk.X, pady=(0, 10))
        
        # Play button
        play_button = tk.Button(
            entry_frame,
            text="Play Video",
            font=("Helvetica", 10),
            command=lambda path=video_path: self.show_playback_screen(path),
            bg="#2196F3",
            fg="white",
            width=15
        )
        play_button.pack(pady=5)

def main():
    try:
        # Display instructions for potential issues
        print("\n=== Emotional Journal App ===")
        print("If you encounter camera issues when running this app, try:")
        print("1. Make sure your webcam is not in use by another application")
        print("2. Check if you have proper permissions to access the camera")
        print("===============================\n")
        
        root = tk.Tk()
        app = EmotionalJournalApp(root)
        root.mainloop()
        
    except Exception as e:
        print(f"\nError running application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
