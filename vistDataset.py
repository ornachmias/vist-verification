import os
import json
import logging
import random

from storyInSequence import StoryInSequence

import logHandler


class VistDataset(object):
    def __init__(self, root_path, samples_num=None) -> None:
        self._samples_num = samples_num
        self._root_path = root_path
        self._story_in_sequence = None
        self._logger = logging.getLogger(logHandler.general_logger)
        self._is_loaded = False

    def get_random_story_ids(self, num):
        self._load_data()
        return random.sample(list(self._story_in_sequence.Stories.keys()), num)

    def get_images_ids(self, story_id):
        self._load_data()
        return self._story_in_sequence.Stories[story_id]["img_ids"]

    def _load_data(self):
        if not self._is_loaded:
            self._story_in_sequence = StoryInSequence(images_dir=os.path.join(self._root_path, "images"),
                                                      annotations_dir=os.path.join(self._root_path, "descriptor"))

        if self._samples_num is not None:
            filtered_keys = sorted(self._story_in_sequence.Stories.keys(), key=int)[:self._samples_num]
            self._story_in_sequence.Stories = {k: self._story_in_sequence.Stories[k] for k in filtered_keys}

        self._is_loaded = True

