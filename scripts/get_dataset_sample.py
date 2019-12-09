import os

import configurations
from dataLoader import DataLoader
from hitCounter import HitCounter
from storyInSequence import StoryInSequence
import random

# Script Parameters
from vistDataset import VistDataset

number_of_sequences = 50
configurations.root_data = "../data"

data_loader = DataLoader(root_path=configurations.root_data)
hit_counter = HitCounter(root_path=configurations.root_data, story_max_hits=configurations.max_story_submit)
vist_dataset = VistDataset(configurations.root_data, hit_counter)

story_in_sequence = StoryInSequence(images_dir=os.path.join(configurations.root_data, "images"),
                                    annotations_dir=os.path.join(configurations.root_data, "descriptor"))

all_story_ids = story_in_sequence.Stories.keys()

seq_count = 0
all_image_seq = set()
for s in all_story_ids:
    image_ids = vist_dataset.get_images_ids(s)
    images_seq = ",".join(image_ids)
    if images_seq not in all_image_seq:
        seq_count += 1
        all_image_seq.add(images_seq)

print("Number of unique sequences: {}".format(seq_count))




selected_ids = random.sample(all_story_ids, 50)
print(", ".join(selected_ids))