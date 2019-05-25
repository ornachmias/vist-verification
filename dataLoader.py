import logging
import os

from google_drive_downloader import GoogleDriveDownloader as gdd

import configurations
import logHandler


class DataLoader(object):

    def __init__(self, root_path) -> None:
        self._images_path = os.path.join(root_path, 'images')
        if not os.path.exists(self._images_path):
            os.makedirs(self._images_path)

        self._logger = logging.getLogger(logHandler.general_logger)

    def download_images(self, force_download=False):
        for file_name in configurations.images_download_urls:
            path = os.path.join(self._images_path, file_name)

            if os.path.exists(path) and not force_download:
                continue

            self._download_from_drive(configurations.images_download_urls[file_name], path)

    def download_descriptors(self):
        pass

    def _download_from_drive(self, file_id, dest_path):
        self._logger.info("Starting download file_id={} to dest_path={}".format(file_id, dest_path))
        gdd.download_file_from_google_drive(file_id=file_id, dest_path=dest_path, unzip=True, showsize=True)
        self._logger.info("Finished download file_id={} to dest_path={}".format(file_id, dest_path))

