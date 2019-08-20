import os.path as osp
import json
import numpy as np
import math
from datetime import datetime
from scipy.misc import imread, imresize
import matplotlib.pyplot as plt

# Taken from https://github.com/lichengunc/vist_api/blob/master/vist.py
class StoryInSequence:
    def __init__(self, images_dir, annotations_dir, splits=None):
        """
		The vist_dir should contain images and annotations, which further contain train/val/test.
		We will load train/val/test together on default and add split in albums, and make mapping.
		- albums  = [{id, title, vist_label, description, img_ids, story_ids}]
		- images  = [{id, album_id, datetaken, title, text, tags}]
		- sents   = [{id, story_id, album_id, img_id, order, original_text, text, length}]
		- stories = [{id, story_id, album_id, sent_ids, img_ids}]
		"""
        self.images_dir = images_dir
        self.annotations_dir = annotations_dir

        # Load annotations and add splits to each album
        if not splits:
            splits = ['train', 'val', 'test']
        sis = {'images': [], 'albums': [], 'annotations': []}
        for split in splits:
            b = datetime.now()
            info = json.load(open(osp.join(annotations_dir, 'sis', split + '.story-in-sequence.json')))
            print('sis\'s [%s] loaded. It took %.2f seconds.' % (split, (datetime.now() - b).total_seconds()))
            for album in info['albums']:
                album['split'] = split
            sis['albums'] += info['albums']
            sis['images'] += info['images']
            sis['annotations'] += info['annotations']

        sents = []
        for ann in sis['annotations']:
            # sent = {album_id, img_id, story_id, text, original_text, }
            sent = ann[0].copy()
            sent['id'] = sent.pop('storylet_id')
            sent['order'] = sent.pop('worker_arranged_photo_order')
            sent['img_id'] = sent.pop('photo_flickr_id')
            sent['length'] = len(sent['text'].split())  # add length property
            sents += [sent]

        # make mapping
        print('Make mapping ...')
        self.Albums = {album['id']: album for album in sis['albums']}
        self.Images = {img['id']: img for img in sis['images']}
        self.Sents = {sent['id']: sent for sent in sents}

        # album_id -> img_ids
        album_to_img_ids = {}
        for img in sis['images']:
            album_id = img['album_id']
            img_id = img['id']
            album_to_img_ids[album_id] = album_to_img_ids.get(album_id, []) + [img_id]

        def getDateTime(img_id):
            x = self.Images[img_id]['datetaken']
            return datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

        for album_id, img_ids in album_to_img_ids.items():
            img_ids.sort(key=getDateTime)

        # story_id -> sent_ids
        story_to_sent_ids = {}
        for sent_id, sent in self.Sents.items():
            story_id = sent['story_id']
            story_to_sent_ids[story_id] = story_to_sent_ids.get(story_id, []) + [sent_id]

        def get_order(sent_id):
            return self.Sents[sent_id]['order']

        for story_id, sent_ids in story_to_sent_ids.items():
            sent_ids.sort(key=get_order)

        # album_id -> story_ids
        album_to_story_ids = {}
        for story_id, sent_ids in story_to_sent_ids.items():
            sent = self.Sents[sent_ids[0]]
            album_id = sent['album_id']
            album_to_story_ids[album_id] = album_to_story_ids.get(album_id, []) + [story_id]

        # add to albums (and self.Albums)
        for album in sis['albums']:
            album['img_ids'] = album_to_img_ids[album['id']]
            album['story_ids'] = album_to_story_ids[album['id']]

        # make Stories: {story_id: {id, album_id, sent_ids, img_ids}}
        self.Stories = {story_id: {'id': story_id,
                                   'sent_ids': sent_ids,
                                   'img_ids': [self.Sents[sent_id]['img_id'] for sent_id in sent_ids],
                                   'album_id': self.Sents[sent_ids[0]]['album_id']}
                        for story_id, sent_ids in story_to_sent_ids.items()}

        print('Mapping for [Albums][Images][Stories][Sents] done.')

        # back to albums, images, stories, sents
        self.albums = self.Albums.values()
        self.images = self.Images.values()
        self.stories = self.Stories.values()
        self.sents = self.Sents.values()

    def read_img(self, img_file):
        img_content = imread(img_file)
        if len(img_content.shape) == 2:
            img_content = np.tile(img_content[:, :, np.newaxis], (1, 1, 3))
        img_content = imresize(img_content, (224, 224))
        return img_content

    def show_story(self, story_id, show_image=True, show_sents=True):
        story = self.Stories[story_id]
        sent_ids = story['sent_ids']
        if show_image:
            plt.figure()
            for i, sent_id in enumerate(sent_ids):
                img_id = self.Sents[sent_id]['img_id']
                img = self.Images[img_id]
                album_id = img['album_id']
                split = self.Albums[album_id]['split']
                img_file = osp.join(self.images_dir, split, img_id + '.jpg')
                img_content = self.read_img(img_file)
                ax = plt.subplot(1, len(sent_ids), i + 1)
                ax.imshow(img_content)
                ax.axis('off')
                ax.set_title(str(img_id) + '\n' + img['datetaken'][5:])
            plt.show()
        if show_sents:
            for sent_id in sent_ids:
                sent = self.Sents[sent_id]
                print('%s: img_id[%s], %s' % (sent['order'], sent['img_id'], sent['text']))

    def show_album(self, album_id):
        album = self.Albums[album_id]
        img_ids = album['img_ids']
        plt.figure()
        cols = 5
        rows = math.ceil(len(img_ids) / float(cols))
        for i, img_id in enumerate(img_ids):
            img = self.Images[img_id]
            img_file = osp.join(self.images_dir, album['split'], img_id + '.jpg')
            img_content = self.read_img(img_file)
            ax = plt.subplot(rows, cols, i + 1)
            ax.imshow(img_content)
            ax.axis('off')
            ax.set_title(str(img_id) + '\n' + img['datetaken'][5:])
        plt.show()
