import os
import json
import random

from storyInSequence import StoryInSequence


class VistDataset(object):
    def __init__(self, root_path, hit_counter, samples_num=None) -> None:
        self._samples_num = samples_num
        self._root_path = root_path
        self._story_in_sequence = None
        self._is_loaded = False
        self._hit_counter = hit_counter
        self._load_data()
        self._current_story_index = 0

    def get_random_story_ids(self, num, specific_story_ids):
        self._load_data()
        selected_stories = []
        selected_images = []

        if specific_story_ids is None:
            keys = list(self._story_in_sequence.Stories.keys())
        else:
            keys = specific_story_ids

        i = 0
        while True:
            story_id = keys[self._current_story_index]
            if set(self._story_in_sequence.Stories[story_id]["img_ids"]).isdisjoint(selected_images) \
                    and not self._hit_counter.is_max_hit(story_id):
                selected_stories.append(story_id)
                selected_images.extend(self._story_in_sequence.Stories[story_id]["img_ids"])

            i += 1
            self._current_story_index += 1
            if self._current_story_index == len(keys):
                self._current_story_index = 0

            if len(selected_stories) == num or i == len(keys):
                break

        return selected_stories

    def get_images_ids(self, story_id):
        self._load_data()
        return self._story_in_sequence.Stories[story_id]["img_ids"]

    def get_story_description(self, story_id):
        self._load_data()
        sent_ids = self._story_in_sequence.Stories[story_id]["sent_ids"]
        sents = []
        for sent_id in sent_ids:
            sents.append(self._story_in_sequence.Sents[sent_id])

        description = ""
        for s in sents:
            description += s["original_text"]

        return description

    def _load_data(self):
        if not self._is_loaded:
            self._story_in_sequence = StoryInSequence(images_dir=os.path.join(self._root_path, "images"),
                                                      annotations_dir=os.path.join(self._root_path, "descriptor"))

        if self._samples_num is not None:
            filtered_keys = sorted(self._story_in_sequence.Stories.keys(), key=int)[:self._samples_num]
            self._story_in_sequence.Stories = {k: self._story_in_sequence.Stories[k] for k in filtered_keys}

        self._is_loaded = True

