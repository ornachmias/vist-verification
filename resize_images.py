import os
import sys
from os import listdir
from os.path import isfile, join
from shutil import copyfile

from PIL import Image
from tqdm import tqdm

if len(sys.argv) < 4:
    print('Script usage: python3 <script_path> <source_directory> <dest_directory> <image_size>')
    sys.exit('Not enough input parameters provided.')

print('Running ', sys.argv[0], ' with the following parameters:')
print('source_directory=' + sys.argv[1])
print('dest_directory=' + sys.argv[2])
print('image_size=' + sys.argv[3])

confirm = input('Continue? [y/n] ').lower()

while confirm != 'n' and confirm != 'y':
    confirm = input('Continue? [y/n] ').lower()

if confirm == 'n':
    sys.exit('Cancelled by user, exiting.')

source_directory = sys.argv[1]
dest_directory = sys.argv[2]
image_size = sys.argv[3]

if not os.path.exists(source_directory):
    sys.exit('Source directory does not exists, exiting.')

if not image_size.isdigit():
    sys.exit('Image size parameter is not a positive number, exiting.')

image_size = int(image_size)
image_size = (image_size, image_size)

if not os.path.exists(dest_directory):
    os.makedirs(dest_directory)

files = [f for f in listdir(source_directory) if isfile(join(source_directory, f))]

for f in tqdm(files):
    source_file = join(source_directory, f)
    dest_file = join(dest_directory, f)
    try:
        image = Image.open(source_file)
        image.thumbnail(image_size)
        image.save(dest_file)
    except:
        copyfile(source_file, dest_file)
