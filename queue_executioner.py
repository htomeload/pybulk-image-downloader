from image_download_manager import ImageDownloadManager

class QueueExecutioner:
    def __init__(self):
        self.image_download_manager = ImageDownloadManager()
        self.urls_text = ""
        self.end_index = 0
        self.index = 0
        self.urls_list = []
        self.is_job_done = False

    def get_urls_list(self):
        self.is_job_done = False
        text_to_list = self.urls_text.split("\n")
        return text_to_list

    def reset_queue(self):
        self.index = 0
        self.end_index = 0
        self.urls_text = ""
        self.urls_list = []
        self.is_job_done = True

    def exec_queues(self, text_input: str, callback, target_path: str = "Downloads"):
        if not text_input:
            return

        if self.index == 0:
            self.urls_text = text_input
            self.urls_list = self.get_urls_list()
            self.end_index = len(self.urls_list)

        if self.index < self.end_index:
            print(f"Queue: {self.index + 1}/{self.end_index}")
            self.image_download_manager.download_image(url=self.urls_list[self.index], filename=str(self.index),
                                                       directory=target_path, callback=callback)
            if self.image_download_manager.is_last_file_download_success():
                self.index += 1
        else:
            print("JOB DONE")
            self.reset_queue()
            self.image_download_manager.reset_download_manager()
