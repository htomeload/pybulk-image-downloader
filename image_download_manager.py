from os import makedirs
from os.path import isdir, exists
import requests as r

class ImageDownloadManager:
    def __init__(self):
        self.requests = r
        self.last_file_path = ""
        self.valid_extension_list = ["jpg", "jpeg", "png", "gif", "webp", "avif", "apng", "png", "gif", "ppm", "pgm"]
        self.native_support_extension = ["png", "gif", "ppm", "pgm"]

    def download_image(self, url: str, filename: str, callback, directory: str = ""):
        try:
            if url is None:
                return

            response = self.requests.get(url=url, stream=True)
            response.raise_for_status()

            if not response.ok:
                return

            file_extension = self.get_file_extension(url=url)

            if directory:
                if not isdir(directory):
                    makedirs(directory, exist_ok=True)

            complete_file_path = f"{directory}\\{filename}{file_extension}"

            with open(complete_file_path, mode="wb") as handler:
                for block in response.iter_content(1024):
                    if not block:
                        break

                    handler.write(block)
        except r.exceptions.RequestException as RequestException:
            return
        else:
            self.last_file_path = complete_file_path
            callback(img_path=complete_file_path)

    def get_file_extension(self, url: str):
        try:
            if not url:
                return ".jpg"

            extension = url.split(".")[-1].lower().lstrip(".")

            if not extension:
                return ".jpg"

            if extension not in self.valid_extension_list:
                return ".jpg"
        except AttributeError:
            return ".jpg"
        except IndexError:
            return ".jpg"
        else:
            return f".{extension}"

    def is_last_file_download_success(self):
        return exists(self.last_file_path)