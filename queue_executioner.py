from image_download_manager import ImageDownloadManager
from logs import Logs

class QueueExecutioner:
    logger = Logs()

    def __init__(self):
        self.image_download_manager = ImageDownloadManager()
        self.urls_text = ""
        self.end_index = 0
        self.index = 0
        self.urls_list = []
        self.is_job_done = False

    def get_urls_list(self):
        self.is_job_done = False
        text_to_list = [line.strip() for line in self.urls_text.split('\n') if line.strip()]
        return text_to_list

    def reset_queue(self, is_abort: bool = False):
        self.index = 0
        self.end_index = 0
        self.urls_text = ""
        self.urls_list = []
        self.is_job_done = not is_abort

    def exec_queues(self, text_input: str, callback, target_path: str = "Downloads", thread_event = None):
        if not text_input:
            return

        if self.index == 0:
            self.urls_text = text_input
            self.urls_list = self.get_urls_list()
            self.end_index = len(self.urls_list)

        for item in self.urls_list:
            if thread_event.is_set():
                self.logger.log(f"[INFO] ABORTED!")
                return

            self.logger.log(f"[INFO] Queue: {self.index + 1}/{self.end_index}")
            self.image_download_manager.download_image(url=item, filename=f"image_{str(self.index)}",
                                                       directory=target_path, callback=callback)

            self.index += 1

        self.logger.log("[INFO] JOB DONE")
        self.logger.log("")
        self.reset_queue(is_abort=thread_event.is_set())
        self.image_download_manager.reset_download_manager()
        callback(img_path="")
