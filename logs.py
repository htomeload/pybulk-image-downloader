from os import mkdir
from os.path import isdir, exists

class Logs:
    def __init__(self):
        self.file_path = 'log/log.txt'

        if not isdir('log'):
            mkdir('log')

    def log(self, text: str):
        print(text)
        with open(self.file_path, mode='a') as file:
            file.write(f"{text}\n")
            file.close()

    def clear_log(self):
        with open(self.file_path, mode='w') as file:
            pass
        print("[INFO] Log was cleared")
