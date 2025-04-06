from os import makedirs, remove
from os.path import isdir, exists, abspath
import requests as r
import hashlib

class ImageDownloadManager:
    def __init__(self):
        self.requests = r
        self.last_file_path = ""
        self.valid_extension_list = ["jpg", "jpeg", "png", "gif", "webp", "avif", "apng", "png", "gif", "ppm", "pgm"]
        self.native_support_extension = ["png", "gif", "ppm", "pgm"]
        self.downloaded_files_md5 = set()
        self.download_success = False

    def download_image(self, url: str, filename: str, callback, directory: str = ""):
        try:
            if url is None or len(url) < 1:
                print("[WARNING] URL is none or empty string")
                self.download_success = True
                callback(img_path="")
                return

            with self.requests.get(url=url, stream=True) as response:
                response.raise_for_status()
                md5_hash = hashlib.md5()

                if not response.ok:
                    print("[WARNING] Response not ok")
                    self.download_success = False
                    return

                file_extension = self.get_file_extension(url=url)

                if directory:
                    if not isdir(directory):
                        makedirs(directory, exist_ok=True)

                complete_file_path = f"{directory}\\{filename}{file_extension}"

                with open(complete_file_path, mode="wb") as handler:
                    for block in response.iter_content(1024):
                        if block:
                            md5_hash.update(block)
                            handler.write(block)

            file_md5 = md5_hash.hexdigest()
            if file_md5 in self.downloaded_files_md5:
                print(f"[SKIPPED - DUPLICATE CONTENT] {url}")
                remove(complete_file_path)
        except r.exceptions.RequestException as RequestException:
            print(f"[ERROR] Request exception {url}: ", str(RequestException))
            self.last_file_path = ""
            self.download_success = False
            return
        except Exception as e:
            print(f"[ERROR] Download file failed for {url}: ", str(e))
            self.last_file_path = ""
            self.download_success = False
            return
        else:
            print(f"Downloaded file from url: {url}")
            self.add_downloaded_file_md5(file_path=complete_file_path)
            self.last_file_path = complete_file_path
            self.download_success = True
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

    def add_downloaded_file_md5(self, file_path):
        hasher = hashlib.md5()
        full_path = abspath(file_path)
        with open(full_path, mode="rb") as handler:
            for chunk in iter(lambda: handler.read(4096), b''):
                hasher.update(chunk)

        self.downloaded_files_md5.add(hasher.hexdigest())

    def is_last_file_download_success(self):
        return self.download_success

    def reset_download_manager(self):
        self.last_file_path = ""
        self.downloaded_files_md5 = set()
        self.download_success = False
