# pybulk-image-downloader
A simply bulk image downloader, develop using Python 3 (Version 3.11)

![preview app](https://files.catbox.moe/tm08iz.jpg)

## Download
You can find latest standalone build, ready-to-use in Release section [here](https://github.com/htomeload/pybulk-image-downloader/releases/latest)

## Build from source code
This project using Pillow and requests, use pip to install requires libraries
```
pip install Pillow requests
```

### Code Structure
```
- main.py
  |
  - logs.py
  - ui.py
    |
    - queue_executioner.py
      |
      - image_download_manager.py
```
     
This project divide code into files, main.py only work as launchpad, please check the other files for relevant codes.
