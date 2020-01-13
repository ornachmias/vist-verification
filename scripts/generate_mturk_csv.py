import operator

import configurations
from dataLoader import DataLoader
from hitCounter import HitCounter
from vistDataset import VistDataset
import csv

image_url_template = 'https://vist-verification.tk/images/{}'

data_loader = DataLoader(root_path='../data')
hit_counter = HitCounter(root_path='../data', story_max_hits=configurations.max_story_submit)
vist_dataset = \
    VistDataset(root_path='../data', hit_counter=hit_counter, samples_num=configurations.samples)


def get_image_url(image_id):
    return image_url_template.format(image_id)


albums = vist_dataset.get_albums()
stories = vist_dataset.get_stories()

with open('hit_data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['id', 'album_id', 'story_id_1', 'story_id_1_text',
                     'story_id_2', 'story_id_2_text',
                     'story_id_3', 'story_id_3_text',
                     'img_1', 'img_2', 'img_3', 'img_4', 'img_5'])

    id = 1
    for album_id in albums:
        imgs_seq = {}
        for story_id in albums[album_id]['story_ids']:
            imgs = ",".join(stories[story_id]['img_ids'])
            if imgs not in imgs_seq:
                imgs_seq[imgs] = []

            imgs_seq[imgs].append(story_id)

        selected_seq = max(imgs_seq.items(), key=operator.itemgetter(1))[0]

        csv_line = [id, album_id]

        for story_id in imgs_seq[selected_seq]:
            csv_line.append(story_id)
            csv_line.append(vist_dataset.get_story_description(story_id))

        for i in vist_dataset.get_images_ids(imgs_seq[selected_seq][0]):
            csv_line.append(image_url_template.format(i))

        writer.writerow(csv_line)
        id += 1








