import tkinter
from tkinter import messagebox
from os.path import exists, abspath
from PIL import Image, ImageTk, ImageFile
from queue_executioner import QueueExecutioner
from image_download_manager import ImageDownloadManager

LABEL_FONT = ("Arial", 12)

class UI:
    def __init__(self):
        # To Support load large file or missing blocks img
        ImageFile.LOAD_TRUNCATED_IMAGES = True

        self.queue_executioner = QueueExecutioner()
        self.image_download_manager = ImageDownloadManager()
        self.download_button_enable = True

        self.window = tkinter.Tk()
        self.window.title("PyBulk Image Downloader")
        self.window.config(padx=40, pady=40)

        self.text_editor_input = tkinter.Text(width=100)
        self.urls_list_label = tkinter.Label(text="Enter urls image (one url per line)", font=LABEL_FONT)
        self.downloaded_image_label = tkinter.Label(text="Recently Downloaded", font=LABEL_FONT, anchor="w", width=30)
        self.directory_label = tkinter.Label(text="Download to directory (using \ for sub-directory)", font=LABEL_FONT, anchor="w", width=90)
        self.directory_input = tkinter.Entry(width=135)
        self.directory_input.insert(0, "Downloads")
        self.canvas = tkinter.Canvas(width=320, height=480, background="white")
        self.download_btn = tkinter.Button(text="Download", width=24, command=self.start_download)
        self.recent_downloaded_image = None
        self.messagebox = messagebox

        self.construct_ui()

        self.window.mainloop()

    def construct_ui(self):
        self.urls_list_label.grid(column=0, row=0, columnspan=3)
        self.text_editor_input.grid(column=0, row=1, columnspan=3)
        self.downloaded_image_label.grid(column=4, row=0)
        self.canvas.grid(column=4, row=1, padx=(40, 0))
        self.directory_label.grid(column=0, row=2)
        self.directory_input.grid(column=0, row=3, columnspan=3, pady=20)
        self.download_btn.grid(column=0, row=4)

    def reset_form(self):
        self.text_editor_input.delete(index1=0.0, index2='end-1c')
        self.directory_input.delete(0, tkinter.END)
        self.directory_input.insert(0, "Downloads")
        self.download_btn.config(state="normal")

    def notify_download_complete(self):
        self.messagebox.showinfo(title="Download completed", message="All images was downloaded")

    def start_download(self):
        self.download_btn.config(state="disabled")
        self.queue_executioner.exec_queues(text_input=self.text_editor_input.get(index1=0.0, index2='end-1c'), callback=self.show_recent_downloaded_image, target_path=self.directory_input.get())

        if self.queue_executioner.is_job_done:
            self.notify_download_complete()
            self.reset_form()

    def show_recent_downloaded_image(self, img_path: str):
        if not img_path:
            return

        if not exists(img_path):
            return

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

        self.window.after(1500, self.start_download)
