import os


class HitCounter(object):
    def __init__(self, root_path, story_max_hits):
        self._counter_path = os.path.join(root_path, "HitCounters")

        if not os.path.exists(self._counter_path):
            os.makedirs(self._counter_path)

        self._story_max_hits = story_max_hits

    def is_max_hit(self, story_id):
        story_path = os.path.join(self._counter_path, story_id)
        if not os.path.exists(story_path):
            return False

        f = open(story_path, "r")
        counter = int(f.read())
        f.close()
        if counter < self._story_max_hits:
            return False

        return True

    def add_counter(self, story_id):
        story_path = os.path.join(self._counter_path, story_id)
        current_count = 0

        if os.path.exists(story_path):
            f = open(story_path, "r")
            current_count = int(f.read())
            f.close()

        f = open(story_path, "w")
        f.write(str(current_count + 1))
        f.close()


