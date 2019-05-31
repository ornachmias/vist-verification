import os
import json
import logging

import logHandler


class VistDataset(object):
    def __init__(self, root_path) -> None:
        self._logger = logging.getLogger(logHandler.general_logger)
        self._descriptor_paths = os.path.join(root_path, "descriptor", "sis")
        self._is_loaded = False
        self.data = {"train": [], "val": [], "test": []}

    def initialize(self):
        if not self._is_loaded:
            self._load_descriptors()

        self._is_loaded = True

    def _load_descriptors(self):
        self._logger.info("Loading train descriptor to memory")
        path = os.path.join(self._descriptor_paths, "train.story-in-sequence.json")
        with open(path) as f:
            self.data["train"] = json.load(f)

        self._logger.info("Loading val descriptor to memory")
        path = os.path.join(self._descriptor_paths, "val.story-in-sequence.json")
        with open(path) as f:
            self.data["val"] = json.load(f)

        self._logger.info("Loading test descriptor to memory")
        path = os.path.join(self._descriptor_paths, "test.story-in-sequence.json")
        with open(path) as f:
            self.data["test"] = json.load(f)

        self._logger.info("Done loading descriptors to memory")

