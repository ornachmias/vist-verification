import os


class DataLoader(object):

    def __init__(self, root_path) -> None:
        self._images_path = os.path.join(root_path, "images")
        print("Images path: " + self._images_path)
        if not os.path.exists(self._images_path):
            os.makedirs(self._images_path)

        self._descriptor_path = os.path.join(root_path, "descriptor")
        print("Descriptor path: " + self._descriptor_path)
        if not os.path.exists(self._descriptor_path):
            os.makedirs(self._descriptor_path)

    def load_image(self, image_id):
        image_path = self._find_file(image_id)
        in_file = open(image_path, "rb")
        data = in_file.read()
        in_file.close()
        return data

    def _find_file(self, image_id):
        images_extensions = ["jpg", "jpeg", "gif", "png"]
        images_folders = ["train", "test"]

        for ext in images_extensions:
            for folder in images_folders:
                if os.path.exists(os.path.join(self._images_path, folder, image_id + "." + ext)):
                    return os.path.join(self._images_path, folder, image_id + "." + ext)

        for dirpath, dirnames, filenames in os.walk(self._images_path):
            for filename in filenames:
                if filename.startswith(image_id + '.'):
                    return os.path.join(dirpath, filename)

        print("Cannot find image_id=" + image_id)



