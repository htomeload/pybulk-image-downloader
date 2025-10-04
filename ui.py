import threading
import tkinter
from tkinter import messagebox, ttk
from os.path import exists, abspath
from PIL import Image, ImageTk, ImageFile
from queue_executioner import QueueExecutioner
from image_download_manager import ImageDownloadManager

LABEL_FONT = ("Segoe UI", 12)

# Custom Colors for Modern Look
COLOR_BACKGROUND_MAIN = "#e8e8e8" # Slightly darker background than before, like FDM
COLOR_BACKGROUND_DARK = "#dddddd" # For secondary areas or a potential footer/status bar
COLOR_WHITE = "white"             # Pure white for containers like Text Editor/Canvas
COLOR_ACCENT = "#2898ff"          # The bright blue
COLOR_TEXT_PRIMARY = "#333333"    # Dark gray for main text

class UI:
    def __init__(self):
        # To Support load large file or missing blocks img
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        self.main_thread = None
        self.thread_stop_event = None

        self.queue_executioner = QueueExecutioner()
        self.image_download_manager = ImageDownloadManager()
        self.download_button_enable = True
        self.is_manually_abort = False

        self.window = tkinter.Tk()
        self.window.title("PyBulk Image Downloader")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.style.configure('TEntry',
                             padding=[5, 5],  # Increase padding for a taller, softer input field
                             fieldbackground=COLOR_WHITE,
                             foreground=COLOR_TEXT_PRIMARY,
                             relief='flat',  # Use flat relief
                             borderwidth=1)  # Add a slight border

        self.style.map('TEntry',
                       bordercolor=[('focus', COLOR_ACCENT)])

        self.window.config(padx=40, pady=40, bg=COLOR_BACKGROUND_MAIN)

        self.text_editor_input = tkinter.Text(
            self.window,  # Ensure parent is passed
            width=100,
            bg=COLOR_WHITE,
            fg=COLOR_TEXT_PRIMARY,
            relief=tkinter.FLAT,
            highlightthickness=1,
            highlightbackground=COLOR_BACKGROUND_DARK,  # Subtle border color
            padx=10, pady=10  # Add internal padding for content spacing
        )
        self.urls_list_label = ttk.Label(text="Enter urls image (one url per line)", font=LABEL_FONT, background=COLOR_BACKGROUND_MAIN, foreground=COLOR_TEXT_PRIMARY)
        self.downloaded_image_label = ttk.Label(text="Recently Downloaded", font=LABEL_FONT, anchor="w", width=30, background=COLOR_BACKGROUND_MAIN, foreground=COLOR_TEXT_PRIMARY)
        self.directory_label = ttk.Label(text="Download to directory (If leave blank, default will be 'Downloads')", font=LABEL_FONT, anchor="w", width=70, background=COLOR_BACKGROUND_MAIN, foreground=COLOR_TEXT_PRIMARY)
        self.directory_input = ttk.Entry(width=135)
        self.directory_input.insert(0, "Downloads")
        self.canvas = tkinter.Canvas(width=320, height=480, background=COLOR_WHITE, highlightthickness=1, highlightbackground="#dddddd")

        self.style.configure('Accent.TButton', background=COLOR_ACCENT, foreground=COLOR_WHITE, borderwidth=0,
                             relief="flat", font=LABEL_FONT)
        self.style.map('Accent.TButton', background=[('active', '#59adff')])
        self.style.configure('Secondary.TButton', background='#e0e0e0', foreground=COLOR_TEXT_PRIMARY,
                             borderwidth=1, relief="raised", font=LABEL_FONT)
        self.style.configure('Secondary.TButton',
                             background=COLOR_WHITE,
                             foreground=COLOR_TEXT_PRIMARY,
                             borderwidth=1,
                             relief="flat",  # Changed to flat
                             bordercolor=COLOR_BACKGROUND_DARK,  # Use a subtle border color
                             font=LABEL_FONT)
        self.style.map('Secondary.TButton',
                       background=[('active', COLOR_BACKGROUND_DARK)])

        self.download_btn = ttk.Button(text="Download", width=24, command=self.start_download, style='Accent.TButton')
        self.abort_btn = ttk.Button(text="Abort", width=24, command=self.abort_download, style='Secondary.TButton')
        self.abort_btn.config(state="disabled")
        self.progress_bar = ttk.Progressbar(length=810, style='TProgressbar')
        self.recent_downloaded_image = None
        self.messagebox = messagebox

        self.construct_ui()

        self.window.mainloop()

    def construct_ui(self):
        # 1. Labels: Small top padding for separation
        self.urls_list_label.grid(column=0, row=0, columnspan=3, sticky="W", pady=(10, 5))

        # 2. Text Editor: Sticking to NSEW
        self.text_editor_input.grid(column=0, row=1, columnspan=3, sticky="NSEW")

        # 3. Downloaded Image Label: Remove padx here, let canvas handle the gap
        self.downloaded_image_label.grid(column=4, row=0, padx=(40, 0), pady=(10, 5), sticky="W")
        # 4. Canvas: Add padding on the left to separate from the text area
        self.canvas.grid(column=4, row=1, padx=(40, 0), sticky="NSEW")

        # 5. Directory Label: Separating from the text editor above
        self.directory_label.grid(column=0, row=2, sticky="W", pady=(20, 5))

        # 6. Directory Input: Sticking to EW with minimum vertical padding
        self.directory_input.grid(column=0, row=3, columnspan=3, pady=(0, 20), sticky="EW")

        # 7. Progress Bar: Sticking to EW with standard padding
        self.progress_bar.grid(column=0, row=4, columnspan=3, pady=20, sticky="EW")

        # 8. Buttons: Control alignment and span
        # Download Button: Anchor to the East of its column for a cleaner look
        self.download_btn.config(width=16)  # Reduced width
        self.download_btn.grid(column=0, row=5, pady=(10, 0), sticky="E", padx=(0, 10))

        # Abort Button: Anchor to the West of its column
        self.abort_btn.config(width=16)  # Reduced width
        self.abort_btn.grid(column=1, row=5, pady=(10, 0), sticky="W", padx=(10, 0))

        # Make the columns/rows that contain the expanding elements configurable to expand
        self.window.grid_columnconfigure(0, weight=4)
        # Add weight to column 1 so the gap between buttons expands
        self.window.grid_columnconfigure(1, weight=1)
        self.window.grid_columnconfigure(4, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

    def reset_form(self):
        self.main_thread = None
        self.thread_stop_event = None
        self.abort_btn.config(state="disabled")
        self.text_editor_input.config(state="normal")
        self.directory_input.config(state="normal")
        self.text_editor_input.delete(index1=0.0, index2='end-1c')
        self.directory_input.delete(0, tkinter.END)
        self.directory_input.insert(0, "Downloads")
        self.download_btn.config(state="normal")

    def soft_reset_form(self):
        self.main_thread = None
        self.thread_stop_event = None
        self.text_editor_input.config(state="normal")
        self.directory_input.config(state="normal")
        self.download_btn.config(state="normal")
        self.abort_btn.config(state="disabled")
        self.is_manually_abort = False
        self.queue_executioner.reset_queue()
        self.progress_bar.stop()

    def notify_download_complete(self):
        self.messagebox.showinfo(title="Download completed", message="All images was downloaded")

    def notify_download_abort(self):
        self.messagebox.showinfo(title="Download aborted", message="Download progress was aborted")

    def abort_download(self):
        self.is_manually_abort = True

        if self.thread_stop_event:
            self.thread_stop_event.set()

    def start_download(self):
        self.abort_btn.config(state="normal")
        self.download_btn.config(state="disabled")
        self.text_editor_input.config(state="disabled")
        self.directory_input.config(state="disabled")

        self.thread_stop_event = threading.Event()
        self.main_thread = threading.Thread(
            target=self.queue_executioner.exec_queues,
            args=(self.text_editor_input.get(index1=0.0, index2='end-1c'), self.show_recent_downloaded_image, self.directory_input.get(), self.thread_stop_event),
            daemon=True
        )
        self.main_thread.start()

    def update_progress_bar(self):
        self.progress_bar.config(maximum=self.queue_executioner.end_index)
        self.progress_bar.step(1)

    def show_recent_downloaded_image(self, img_path: str):
        self.window.after(0, self._update_recent_downloaded_image, img_path)

    def _update_recent_downloaded_image(self, img_path: str):
        if self.queue_executioner.is_job_done:
            self.notify_download_complete()
            self.reset_form()

        if self.is_manually_abort:
            self.notify_download_abort()
            self.soft_reset_form()

        if not img_path or not img_path.strip():
            return

        if exists(img_path):
            _width = 0
            _height = 0

            full_path = abspath(img_path)

            image = Image.open(fp=full_path, mode="r")

            self.recent_downloaded_image = ImageTk.PhotoImage(image)

            width, height = image.size

            if width > height:
                _width = 480
                _height = 320
            else:
                _width = 320
                _height = 480

            ratio = min(_width / width, _height / height)
            new_width, new_height = int(width * ratio), int(height * ratio)

            # Resize the image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # Convert to Tkinter-compatible format
            self.recent_downloaded_image = ImageTk.PhotoImage(image)

            # Clear canvas and place new image centered
            self.canvas.delete("all")
            self.canvas.create_image(_width // 2, _height // 2, image=self.recent_downloaded_image,
                                     anchor="center")

            self.update_progress_bar()
