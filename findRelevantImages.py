import os

import configurations
from dataLoader import DataLoader
from vistDataset import VistDataset
from shutil import copyfile

data_loader = DataLoader(root_path="./data")
vist_dataset = VistDataset(root_path="./data", samples_num=configurations.samples)
data_loader.initialize()
vist_dataset.initialize()

story_ids = vist_dataset._story_in_sequence.Stories.keys()
dst_directory = "./data/images/train"

for story_id in story_ids:
    images_ids = vist_dataset.get_images_ids(story_id)
    for image_id in images_ids:
        p = data_loader._find_file(image_id)
        filename = os.path.basename(p)
        copyfile(p, os.path.join(dst_directory, filename))






