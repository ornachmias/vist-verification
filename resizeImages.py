import os
from os.path import isfile, join
from tqdm import tqdm

from pil import Image

# image_paths = [join('./data/images/train', f) for f in os.listdir('./data/images/train') if isfile(join('./data/images/train', f)) and (not f.endswith('.thumbnail.jpeg') and not f.endswith('.thumbnail.png'))]
#
# for image_path in tqdm(image_paths):
#     if image_path.endswith(".png"):
#         im = Image.open(image_path)
#         im.thumbnail([300, 300])
#         im.save(image_path + ".thumbnail.png")
#         continue
#
#     if not os.path.exists(image_path + ".thumbnail.jpeg"):
#         im = Image.open(image_path)
#         im.thumbnail([300, 300])
#         im.save(image_path + ".thumbnail.jpeg")


# image_paths = [join('./data/images/train', f) for f in os.listdir('./data/images/train') if isfile(join('./data/images/train', f)) and 'thumbnail' not in f]
# for image_path in tqdm(image_paths):
#     os.remove(image_path)