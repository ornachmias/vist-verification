import os
import time
import pickle


class DataLoader(object):
    def __init__(self, root_path) -> None:
        self._result_path = os.path.join(root_path, "results", "captions")
        self._images_path = os.path.join(root_path, "images")
        print("Images path: " + self._images_path)
        if not os.path.exists(self._images_path):
            os.makedirs(self._images_path)

        self._descriptor_path = os.path.join(root_path, "descriptor")
        print("Descriptor path: " + self._descriptor_path)
        if not os.path.exists(self._descriptor_path):
            os.makedirs(self._descriptor_path)

    def load_image(self, image_id):
        current_time = time.time()
        image_path = self._find_file(image_id)
        if image_path is None:
            return None
        print("Finding the file took", str(time.time() - current_time))
        current_time = time.time()
        in_file = open(image_path, "rb")
        data = in_file.read()
        in_file.close()
        print("Loading the file took", str(time.time() - current_time))
        return data

    def save_story_result(self, story_id, img_ids, captions, features):
        story_path = os.path.join(self._result_path, story_id)
        img_ids_path = os.path.join(story_path, "img_ids")
        with open(img_ids_path, 'a+') as f:
            for i in img_ids:
                f.write(i + "\n")

            f.close()

        captions_path = os.path.join(story_path, "captions")
        with open(captions_path, 'a+') as f:
            for c in captions:
                f.write(c + "\n")

            f.close()

        pickle.dump(features, open(os.path.join(story_path, "features.pkl"), "wb"))

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



