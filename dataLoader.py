import logging
import os
import urllib.request
import tarfile

from google_drive_downloader import GoogleDriveDownloader as gdd

import configurations
import logHandler


class DataLoader(object):

    def __init__(self, root_path) -> None:
        self._images_path = os.path.join(root_path, "images")
        if not os.path.exists(self._images_path):
            os.makedirs(self._images_path)

        self._descriptor_path = os.path.join(root_path, "descriptor")
        if not os.path.exists(self._descriptor_path):
            os.makedirs(self._descriptor_path)

        self._logger = logging.getLogger(logHandler.general_logger)

    def initialize(self):
        paths = []
        for file_name in configurations.images_download_ids:
            continue
            paths.append(self._download_images(file_name))

        paths.append(self._download_descriptors())

        # for path in paths:
        #     self._extract_file(path)

    def load_image(self, image_id):
        image_path = self._find_file(image_id)
        in_file = open(image_path, "rb")
        data = in_file.read()
        in_file.close()
        return data

    def _find_file(self, image_id):
        for dirpath, dirnames, filenames in os.walk(self._images_path):
            for filename in filenames:
                if os.path.splitext(filename)[0].startswith(image_id + '.'):
                    return os.path.join(dirpath, filename)

    def _download_images(self, file_name, force_download=False):
        path = os.path.join(self._images_path, file_name)

        if os.path.exists(path) and not force_download:
            self._logger.info("File '{}' already exists and force_download=False, skipping download.".format(path))
            return path

        self._download_from_drive(configurations.images_download_ids[file_name], path)
        return path

    def _download_descriptors(self, force_download=False):
        path = os.path.join(self._descriptor_path, configurations.descriptors_file)
        if os.path.exists(path) and not force_download:
            self._logger.info("File '{}' already exists and force_download=False, skipping download.".format(path))
            return path

        self._logger.info("Starting download from '{}'".format(configurations.descriptors_url))
        urllib.request.urlretrieve(configurations.descriptors_url, path)
        self._logger.info("Download completed to path '{}'".format(path))
        return path

    def _download_from_drive(self, file_id, dest_path):
        self._logger.info("Starting download file_id={} to dest_path={}".format(file_id, dest_path))
        gdd.download_file_from_google_drive(file_id=file_id, dest_path=dest_path, unzip=False, showsize=True)
        self._logger.info("Finished download file_id={} to dest_path={}".format(file_id, dest_path))

    def _extract_file(self, path):
        self._logger.info("Extracting {}".format(path))
        tar = tarfile.open(path, "r:gz")
        tar.extractall(path=os.path.dirname(path))
        tar.close()
        self._logger.info("Done extracting {}".format(path))


