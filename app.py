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

# Modern UI color scheme
COLORS = {
    "primary": "#4361EE",     # Primary accent color
    "secondary": "#3F37C9",   # Secondary accent color
    "accent": "#4CC9F0",      # Highlights
    "light": "#F8F9FA",       # Light background
    "dark": "#212529",        # Dark text
    "success": "#4CAF50",     # Success color
    "warning": "#FF9800",     # Warning color
    "error": "#F44336",       # Error color
    "light_accent": "#E9ECEF", # Light accent for card backgrounds
    "border": "#DEE2E6"       # Border color
}

class ModernButton(tk.Button):
    """A modern styled button with hover effects"""
    def __init__(self, master=None, **kwargs):
        self.bg_color = kwargs.pop('bg', COLORS["primary"])
        self.hover_color = kwargs.pop('hover_color', COLORS["secondary"])
        self.fg_color = kwargs.pop('fg', "white")
        
        # Set modern styling
        kwargs['bg'] = self.bg_color
        kwargs['fg'] = self.fg_color
        kwargs['relief'] = tk.FLAT
        kwargs['borderwidth'] = 0
        kwargs['padx'] = 15
        kwargs['pady'] = 8
        kwargs['font'] = ('Helvetica', 10, 'bold')
        
        super().__init__(master, **kwargs)
        
        # Configure hover events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, e):
        self.config(bg=self.hover_color)
    
    def _on_leave(self, e):
        self.config(bg=self.bg_color)

class ModernFrame(tk.Frame):
    """A modern frame with optional shadow effect"""
    def __init__(self, master=None, has_shadow=False, **kwargs):
        bg_color = kwargs.pop('bg', COLORS["light"])
        kwargs['bg'] = bg_color
        
        if 'padx' not in kwargs:
            kwargs['padx'] = 15
        
        if 'pady' not in kwargs:
            kwargs['pady'] = 15
        
        if 'relief' not in kwargs and has_shadow:
            kwargs['relief'] = tk.RAISED
            kwargs['borderwidth'] = 1
        
        super().__init__(master, **kwargs)

class EmotionalJournalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Emotional Journal")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        self.root.configure(bg=COLORS["light"])
        
        # Apply a modern look to Ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme as base
        
        # Configure combobox style
        self.style.configure('TCombobox', 
                            fieldbackground=COLORS["light"],
                            background=COLORS["light_accent"])
        
        # Configure scrollbar style
        self.style.configure('TScrollbar',
                           troughcolor=COLORS["light"], 
                           background=COLORS["primary"])
        
        # Create frames for each "screen"
        self.main_frame = ModernFrame(root, bg=COLORS["light"])
        self.record_frame = ModernFrame(root, bg=COLORS["light"])
        self.history_frame = ModernFrame(root, bg=COLORS["light"])
        self.playback_frame = ModernFrame(root, bg=COLORS["light"])
        
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
        # Logo/icon at the top
        logo_frame = ModernFrame(self.main_frame, bg=COLORS["light"])
        logo_frame.pack(pady=(40, 20))
        
        # Create a circle for the logo
        logo_canvas = tk.Canvas(logo_frame, width=100, height=100, bg=COLORS["light"], highlightthickness=0)
        logo_canvas.create_oval(10, 10, 90, 90, fill=COLORS["primary"], outline="")
        logo_canvas.create_text(50, 50, text="EJ", font=("Helvetica", 36, "bold"), fill="white")
        logo_canvas.pack()
        
        # App title in a modern font
        title_label = tk.Label(
            self.main_frame, 
            text="Emotional Journal",
            font=("Helvetica", 28, "bold"),
            bg=COLORS["light"],
            fg=COLORS["dark"],
            pady=10
        )
        title_label.pack()
        
        # Subtitle with app description
        description = tk.Label(
            self.main_frame,
            text="Record your emotional state and journal your thoughts",
            font=("Helvetica", 12),
            bg=COLORS["light"],
            fg=COLORS["dark"],
            pady=5
        )
        description.pack()
        
        # Container for buttons with some space
        button_container = ModernFrame(self.main_frame, bg=COLORS["light"], pady=40)
        button_container.pack()
        
        # Record button with icon indicator
        record_frame = ModernFrame(button_container, bg=COLORS["light"], pady=10)
        record_frame.pack()
        
        record_icon = tk.Canvas(record_frame, width=24, height=24, bg=COLORS["light"], highlightthickness=0)
        record_icon.create_oval(4, 4, 20, 20, fill=COLORS["error"], outline="")
        record_icon.grid(row=0, column=0, padx=(0, 10))
        
        record_button = ModernButton(
            record_frame,
            text="Record New Entry",
            command=self.show_record_screen,
            bg=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=20,
        )
        record_button.grid(row=0, column=1)
        
        # History button with icon
        history_frame = ModernFrame(button_container, bg=COLORS["light"], pady=10)
        history_frame.pack()
        
        history_icon = tk.Canvas(history_frame, width=24, height=24, bg=COLORS["light"], highlightthickness=0)
        history_icon.create_rectangle(4, 4, 20, 20, fill=COLORS["accent"], outline="")
        history_icon.grid(row=0, column=0, padx=(0, 10))
        
        view_button = ModernButton(
            history_frame,
            text="View Past Entries",
            command=self.show_history_screen,
            bg=COLORS["accent"],
            hover_color=COLORS["secondary"],
            width=20,
        )
        view_button.grid(row=0, column=1)
    
    def setup_record_screen(self):
        # Top navigation bar with title and back button
        nav_bar = ModernFrame(self.record_frame, bg=COLORS["primary"], pady=10)
        nav_bar.pack(fill=tk.X)
        
        back_btn = ModernButton(
            nav_bar,
            text="← Back",
            command=self.show_main_screen,
            bg=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=8
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Title in the navigation bar
        title_label = tk.Label(
            nav_bar, 
            text="Record a New Journal Entry",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["primary"],
            fg="white",
        )
        title_label.pack(side=tk.LEFT, expand=True)
        
        # Content area with form
        content_frame = ModernFrame(self.record_frame, bg=COLORS["light"], padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Form container with card-like appearance
        form_card = ModernFrame(
            content_frame, 
            bg=COLORS["light_accent"], 
            has_shadow=True,
            padx=20,
            pady=20
        )
        form_card.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Title input with label
        title_label = tk.Label(
            form_card, 
            text="Title (required)",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["light_accent"],
            fg=COLORS["dark"],
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 5))
        
        self.title_entry = tk.Entry(
            form_card, 
            font=("Helvetica", 12),
            bg="white",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["primary"]
        )
        self.title_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Emotion selection
        emotion_label = tk.Label(
            form_card, 
            text="How are you feeling?",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["light_accent"],
            fg=COLORS["dark"],
            anchor="w"
        )
        emotion_label.pack(anchor="w", pady=(0, 5))
        
        self.emotion_var = tk.StringVar(value="Happy")
        emotions = ["Happy", "Sad", "Anxious", "Calm", "Angry", "Grateful", "Confused", "Other"]
        
        emotion_frame = ModernFrame(form_card, bg=COLORS["light_accent"], pady=0)
        emotion_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Create a row of emotion buttons instead of a dropdown
        for i, emotion in enumerate(emotions):
            bg_color = COLORS["light"] if emotion != "Happy" else COLORS["primary"]
            fg_color = COLORS["dark"] if emotion != "Happy" else "white"
            
            btn = tk.Button(
                emotion_frame,
                text=emotion,
                bg=bg_color,
                fg=fg_color,
                relief=tk.FLAT,
                bd=0,
                padx=10,
                pady=5,
                font=("Helvetica", 10),
                command=lambda e=emotion: self.select_emotion(e)
            )
            row = i // 4
            col = i % 4
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        for i in range(4):
            emotion_frame.grid_columnconfigure(i, weight=1)
        
        # Journal text
        journal_label = tk.Label(
            form_card, 
            text="Write your thoughts (optional)",
            font=("Helvetica", 12, "bold"),
            bg=COLORS["light_accent"],
            fg=COLORS["dark"],
            anchor="w"
        )
        journal_label.pack(anchor="w", pady=(0, 5))
        
        self.journal_text = scrolledtext.ScrolledText(
            form_card, 
            font=("Helvetica", 12),
            height=4,
            relief=tk.FLAT,
            bd=1,
            bg="white"
        )
        self.journal_text.pack(fill=tk.X, pady=(0, 15))
        
        # Controls at the bottom
        controls_card = ModernFrame(
            content_frame, 
            bg=COLORS["light_accent"], 
            has_shadow=True,
            padx=20,
            pady=20
        )
        controls_card.pack(fill=tk.X, pady=10)
        
        # Title for controls
        controls_title = tk.Label(
            controls_card,
            text="Recording Controls",
            font=("Helvetica", 14, "bold"),
            bg=COLORS["light_accent"],
            fg=COLORS["dark"],
        )
        controls_title.pack(pady=(0, 15))
        
        # Recording indicator
        self.recording_indicator_frame = tk.Frame(controls_card, bg=COLORS["light_accent"])
        self.recording_indicator_frame.pack(pady=(0, 15))
        
        self.recording_indicator = tk.Canvas(
            self.recording_indicator_frame, 
            width=20, 
            height=20, 
            bg=COLORS["light_accent"], 
            highlightthickness=0
        )
        self.recording_indicator.create_oval(2, 2, 18, 18, fill="#cccccc", tags="indicator")
        self.recording_indicator.pack(side=tk.LEFT, padx=(0, 10))
        
        self.recording_status = tk.Label(
            self.recording_indicator_frame,
            text="Not Recording",
            font=("Helvetica", 10),
            bg=COLORS["light_accent"],
            fg="#666666"
        )
        self.recording_status.pack(side=tk.LEFT)
        
        # Button controls in a row with larger buttons
        button_frame = tk.Frame(controls_card, bg=COLORS["light_accent"])
        button_frame.pack(fill=tk.X, pady=10)
        
        # Create a 3-column grid for buttons
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        # Start recording button
        self.start_button = ModernButton(
            button_frame,
            text="▶ START RECORDING",
            command=self.toggle_recording,
            bg=COLORS["error"],
            hover_color="#D32F2F",
            width=18,
            font=('Helvetica', 12, 'bold'),
            pady=12
        )
        self.start_button.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Stop recording button
        self.stop_button = ModernButton(
            button_frame,
            text="■ STOP RECORDING",
            command=self.stop_recording,
            state=tk.DISABLED,
            bg=COLORS["warning"],
            hover_color="#F57C00",
            width=18,
            font=('Helvetica', 12, 'bold'),
            pady=12
        )
        self.stop_button.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        # Save button
        self.save_button = ModernButton(
            button_frame,
            text="💾 SAVE JOURNAL",
            command=self.save_recording,
            state=tk.DISABLED,
            bg=COLORS["success"],
            hover_color="#388E3C",
            width=18,
            font=('Helvetica', 12, 'bold'),
            pady=12
        )
        self.save_button.grid(row=0, column=2, padx=10, pady=5, sticky="ew")
        
        # Add tooltips/hints below buttons
        hints_frame = tk.Frame(controls_card, bg=COLORS["light_accent"])
        hints_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Match the grid layout of the buttons
        hints_frame.columnconfigure(0, weight=1)
        hints_frame.columnconfigure(1, weight=1)
        hints_frame.columnconfigure(2, weight=1)
        
        tk.Label(
            hints_frame, 
            text="Begin capturing video", 
            font=("Helvetica", 9), 
            fg="#666666",
            bg=COLORS["light_accent"]
        ).grid(row=0, column=0, padx=10)
        
        tk.Label(
            hints_frame, 
            text="End video recording", 
            font=("Helvetica", 9), 
            fg="#666666",
            bg=COLORS["light_accent"]
        ).grid(row=0, column=1, padx=10)
        
        tk.Label(
            hints_frame, 
            text="Store video and notes", 
            font=("Helvetica", 9), 
            fg="#666666",
            bg=COLORS["light_accent"]
        ).grid(row=0, column=2, padx=10)

    def select_emotion(self, emotion):
        """Update the selected emotion"""
        self.emotion_var.set(emotion)
        
        # Update all emotion buttons
        for widget in self.record_frame.winfo_children():
            if isinstance(widget, ModernFrame):
                for card in widget.winfo_children():
                    if isinstance(card, ModernFrame) and card.winfo_children():
                        for frame in card.winfo_children():
                            if isinstance(frame, ModernFrame):
                                for btn in frame.winfo_children():
                                    if isinstance(btn, tk.Button) and btn.cget('text') in ["Happy", "Sad", "Anxious", "Calm", "Angry", "Grateful", "Confused", "Other"]:
                                        if btn.cget('text') == emotion:
                                            btn.config(bg=COLORS["primary"], fg="white")
                                        else:
                                            btn.config(bg=COLORS["light"], fg=COLORS["dark"])
    
    def setup_history_screen(self):
        # Top navigation bar with title and back button
        nav_bar = ModernFrame(self.history_frame, bg=COLORS["primary"], pady=10)
        nav_bar.pack(fill=tk.X)
        
        back_btn = ModernButton(
            nav_bar,
            text="← Back",
            command=self.show_main_screen,
            bg=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=8
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Title in the navigation bar
        title_label = tk.Label(
            nav_bar, 
            text="Journal History",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["primary"],
            fg="white",
        )
        title_label.pack(side=tk.LEFT, expand=True)
        
        # Content area
        content_frame = ModernFrame(self.history_frame, bg=COLORS["light"], padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollable container for journal entries
        self.entries_container = ModernFrame(content_frame, bg=COLORS["light"], pady=0)
        self.entries_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for scrolling
        canvas_frame = tk.Frame(self.entries_container, bg=COLORS["light"])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(
            canvas_frame, 
            bg=COLORS["light"],
            bd=0,
            highlightthickness=0
        )
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS["light"])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
    
    def setup_playback_screen(self):
        # Top navigation bar with title and back button
        nav_bar = ModernFrame(self.playback_frame, bg=COLORS["primary"], pady=10)
        nav_bar.pack(fill=tk.X)
        
        back_btn = ModernButton(
            nav_bar,
            text="← Back",
            command=self.show_history_screen,
            bg=COLORS["primary"],
            hover_color=COLORS["secondary"],
            width=8
        )
        back_btn.pack(side=tk.LEFT, padx=10)
        
        # Title in the navigation bar
        self.playback_title = tk.Label(
            nav_bar, 
            text="Playing Journal Entry",
            font=("Helvetica", 16, "bold"),
            bg=COLORS["primary"],
            fg="white",
        )
        self.playback_title.pack(side=tk.LEFT, expand=True)
        
        # Content area
        content_frame = ModernFrame(self.playback_frame, bg=COLORS["light"], padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card with info
        info_card = ModernFrame(
            content_frame, 
            bg=COLORS["light_accent"], 
            has_shadow=True,
            padx=30,
            pady=30
        )
        info_card.pack(fill=tk.BOTH, expand=True)
        
        # Video playing icon
        video_icon = tk.Canvas(info_card, width=80, height=80, bg=COLORS["light_accent"], highlightthickness=0)
        video_icon.create_oval(10, 10, 70, 70, fill=COLORS["accent"], outline="")
        video_icon.create_polygon(30, 25, 30, 55, 60, 40, fill="white")
        video_icon.pack(pady=20)
        
        # Message
        message = tk.Label(
            info_card,
            text="Your video is playing in your default video player",
            font=("Helvetica", 14),
            bg=COLORS["light_accent"],
            fg=COLORS["dark"],
            pady=20
        )
        message.pack()
        
        note = tk.Label(
            info_card,
            text="When you're done watching, you can close the player and return here.",
            font=("Helvetica", 10),
            bg=COLORS["light_accent"],
            fg="#666666",
            pady=10
        )
        note.pack()
    
    # Recording functions
    def toggle_recording(self):
        if not self.title_entry.get():
            messagebox.showerror("Error", "Please enter a title for your journal entry.")
            return
        
        if not self.recording:
            # Start recording
            self.recording = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            
            # Update recording indicator
            self.recording_indicator.itemconfig("indicator", fill=COLORS["error"])
            self.recording_status.config(text="Recording...", fg=COLORS["error"])
            self.blink_recording_indicator()
            
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
            
            # Create a new popup window for the camera display
            self.create_camera_window()
                
            # Start capture thread
            self.frames = []
            self.capture_thread = threading.Thread(target=self.capture_frames)
            self.capture_thread.daemon = True
            self.capture_thread.start()
    
    def blink_recording_indicator(self):
        """Create a blinking effect for the recording indicator"""
        if not self.recording:
            # Stop blinking if not recording
            self.recording_indicator.itemconfig("indicator", fill="#cccccc")
            return
            
        # Toggle between red and darker red
        current_color = self.recording_indicator.itemcget("indicator", "fill")
        new_color = "#990000" if current_color == COLORS["error"] else COLORS["error"]
        self.recording_indicator.itemconfig("indicator", fill=new_color)
        
        # Schedule the next blink
        self.root.after(500, self.blink_recording_indicator)

    def create_camera_window(self):
        """Create a separate window for camera display"""
        self.camera_window = tk.Toplevel(self.root)
        self.camera_window.title("Camera - Recording")
        self.camera_window.geometry("800x600")
        self.camera_window.protocol("WM_DELETE_WINDOW", self.on_camera_window_close)
        
        # Create a container for the camera feed
        camera_container = tk.Frame(self.camera_window, bg=COLORS["dark"])
        camera_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create the preview label
        self.preview_label = tk.Label(camera_container, bg=COLORS["dark"])
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        # Controls at the bottom
        control_frame = tk.Frame(self.camera_window, bg=COLORS["light"], pady=10)
        control_frame.pack(fill=tk.X)
        
        # Recording indicator
        indicator_frame = tk.Frame(control_frame, bg=COLORS["light"])
        indicator_frame.pack(pady=(0, 10))
        
        recording_dot = tk.Canvas(
            indicator_frame, 
            width=20, 
            height=20, 
            bg=COLORS["light"], 
            highlightthickness=0
        )
        recording_dot.create_oval(2, 2, 18, 18, fill=COLORS["error"], tags="indicator")
        recording_dot.pack(side=tk.LEFT, padx=(0, 10))
        
        recording_text = tk.Label(
            indicator_frame,
            text="RECORDING",
            font=("Helvetica", 10, "bold"),
            bg=COLORS["light"],
            fg=COLORS["error"]
        )
        recording_text.pack(side=tk.LEFT)
        
        # Add buttons for quick access
        button_frame = tk.Frame(control_frame, bg=COLORS["light"])
        button_frame.pack(fill=tk.X, padx=20)
        
        stop_btn = ModernButton(
            button_frame,
            text="■ STOP RECORDING",
            command=self.stop_recording,
            bg=COLORS["warning"],
            hover_color="#F57C00",
            width=18,
            font=('Helvetica', 12, 'bold'),
            pady=12
        )
        stop_btn.pack(side=tk.LEFT, padx=10)
        
        save_btn = ModernButton(
            button_frame,
            text="💾 SAVE JOURNAL",
            command=self.save_recording,
            bg=COLORS["success"],
            hover_color="#388E3C",
            width=18,
            font=('Helvetica', 12, 'bold'),
            pady=12
        )
        save_btn.pack(side=tk.RIGHT, padx=10)
        
        # Start updating the camera feed
        self.update_preview()
    
    def on_camera_window_close(self):
        """Handle the camera window being closed by the user"""
        self.stop_recording()
        if hasattr(self, 'camera_window'):
            self.camera_window.destroy()
            
    def update_preview(self):
        """Update the preview image in the camera window"""
        if not hasattr(self, 'camera_window') or not self.camera_window.winfo_exists():
            return
            
        if self.recording and self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    # Convert to format Tkinter can display
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = PIL.Image.fromarray(frame)
                    
                    # Get the current size of the preview label
                    width = self.preview_label.winfo_width()
                    height = self.preview_label.winfo_height()
                    
                    # Use default size if widget not properly sized yet
                    if width < 10:
                        width = 640
                        height = 480
                    
                    # Maintain aspect ratio
                    img_ratio = frame.shape[1] / frame.shape[0]
                    if width / height > img_ratio:
                        new_width = int(height * img_ratio)
                        new_height = height
                    else:
                        new_width = width
                        new_height = int(width / img_ratio)
                    
                    # Resize the image
                    img = img.resize((new_width, new_height), PIL.Image.LANCZOS)
                    
                    # Keep a reference to avoid garbage collection
                    self.photo = PIL.ImageTk.PhotoImage(image=img)
                    self.preview_label.config(image=self.photo)
                    
                    # Schedule the next update
                    self.camera_window.after(30, self.update_preview)
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
        
        # Close camera window if open
        if hasattr(self, 'camera_window') and self.camera_window.winfo_exists():
            self.camera_window.destroy()
        
        # Update UI
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.recording_indicator.itemconfig("indicator", fill="#cccccc")
        self.recording_status.config(text="Stopped", fg="#666666")
    
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
        # Update recording indicator
        self.recording_indicator.itemconfig("indicator", fill="#4CAF50")  # Green for success
        self.recording_status.config(text="Saved", fg=COLORS["success"])
        # Reset after 2 seconds
        self.root.after(2000, lambda: self.recording_status.config(text="Not Recording", fg="#666666"))
        self.root.after(2000, lambda: self.recording_indicator.itemconfig("indicator", fill="#cccccc"))
        
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
            empty_state = ModernFrame(self.scrollable_frame, bg=COLORS["light"], pady=40)
            empty_state.pack(fill=tk.X)
            
            # Placeholder icon
            icon_canvas = tk.Canvas(empty_state, width=80, height=80, bg=COLORS["light"], highlightthickness=0)
            icon_canvas.create_rectangle(20, 20, 60, 60, fill=COLORS["light_accent"], outline="")
            icon_canvas.create_line(30, 35, 50, 35, fill=COLORS["dark"], width=2)
            icon_canvas.create_line(30, 45, 50, 45, fill=COLORS["dark"], width=2)
            icon_canvas.pack()
            
            no_entries = tk.Label(
                empty_state,
                text="No journal entries found yet",
                font=("Helvetica", 14, "bold"),
                bg=COLORS["light"],
                fg=COLORS["dark"],
                pady=10
            )
            no_entries.pack()
            
            suggestion = tk.Label(
                empty_state,
                text="Record your first entry to see it here",
                font=("Helvetica", 12),
                bg=COLORS["light"],
                fg="#666666",
                pady=5
            )
            suggestion.pack()
            
            record_btn = ModernButton(
                empty_state,
                text="Record a New Entry",
                command=self.show_record_screen,
                bg=COLORS["primary"],
                hover_color=COLORS["secondary"],
                width=20
            )
            record_btn.pack(pady=20)
            
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
        
        # Create entry widget with modern card design
        entry_card = ModernFrame(
            self.scrollable_frame,
            bg="white",
            has_shadow=True,
            padx=20,
            pady=20
        )
        entry_card.pack(fill=tk.X, pady=10, padx=10)
        
        # Header with emotional indicator
        header_frame = tk.Frame(entry_card, bg="white")
        header_frame.pack(fill=tk.X)
        
        # Colored emotion indicator
        emotion_color = COLORS["primary"]  # Default color
        if emotion.lower() == "happy":
            emotion_color = "#4CAF50"  # Green for happy
        elif emotion.lower() == "sad":
            emotion_color = "#2196F3"  # Blue for sad
        elif emotion.lower() == "anxious":
            emotion_color = "#FF9800"  # Orange for anxious
        elif emotion.lower() == "angry":
            emotion_color = "#F44336"  # Red for angry
        
        emotion_indicator = tk.Frame(header_frame, bg=emotion_color, width=4, height=24)
        emotion_indicator.pack(side=tk.LEFT, padx=(0, 15))
        
        title_label = tk.Label(
            header_frame, 
            text=title,
            font=("Helvetica", 16, "bold"),
            bg="white",
            fg=COLORS["dark"],
            anchor="w"
        )
        title_label.pack(side=tk.LEFT, fill=tk.X)
        
        # Date in subtle styling
        date_label = tk.Label(
            entry_card, 
            text=date,
            font=("Helvetica", 10, "italic"),
            bg="white",
            fg="#666666",
            anchor="w"
        )
        date_label.pack(fill=tk.X, pady=(5, 10))
        
        # Emotion tag with color
        emotion_tag = tk.Label(
            entry_card,
            text=f"Feeling: {emotion}",
            font=("Helvetica", 10),
            bg=emotion_color,
            fg="white",
            padx=8,
            pady=3
        )
        emotion_tag.pack(side=tk.LEFT, anchor="w", pady=(0, 15))
        
        # Main content area
        content_frame = tk.Frame(entry_card, bg="white")
        content_frame.pack(fill=tk.X, pady=10)
        
        # Content preview (if available)
        if journal_content:
            # Limit to 150 chars
            preview = journal_content[:150] + ("..." if len(journal_content) > 150 else "")
            content_label = tk.Label(
                content_frame, 
                text=preview,
                font=("Helvetica", 11),
                bg="white",
                fg=COLORS["dark"],
                anchor="w",
                justify=tk.LEFT,
                wraplength=600
            )
            content_label.pack(fill=tk.X)
        
        # Action buttons
        button_frame = tk.Frame(entry_card, bg="white")
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        play_button = ModernButton(
            button_frame,
            text="Play Video",
            command=lambda path=video_path: self.show_playback_screen(path),
            bg=COLORS["primary"],
            hover_color=COLORS["secondary"]
        )
        play_button.pack(side=tk.RIGHT)

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
