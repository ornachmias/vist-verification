import os

import configurations
from clint.textui import progress
import requests


class DataLoader(object):

    def __init__(self, root_path, logger) -> None:
        super().__init__()
        self._root_path = root_path
        self._logger = logger

    def download_images(self):
        for file_name in configurations.images_download_urls:
            r = requests.get(configurations.images_download_urls[file_name], stream=True)
            path = os.path.join(self._root_path, file_name)
            self._logger.info("Starting download '{}' to '{}'"
                              .format(configurations.images_download_urls[file_name], path))
            with open(path, 'wb') as f:
                total_length = int(r.headers.get("content-length"))
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length / 1024) + 1):
                    if chunk:
                        f.write(chunk)
                        f.flush()

            self._logger.info("Done downloading '{}' to '{}'"
                              .format(configurations.images_download_urls[file_name], path))

    def download_descriptors(self):
        pass

