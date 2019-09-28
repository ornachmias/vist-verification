import os


class DataLoader(object):

    def __init__(self, root_path) -> None:
        self._images_path = os.path.join(root_path, "images")
        if not os.path.exists(self._images_path):
            os.makedirs(self._images_path)

        self._descriptor_path = os.path.join(root_path, "descriptor")
        if not os.path.exists(self._descriptor_path):
            os.makedirs(self._descriptor_path)

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



