import logging


class LogHandler(object):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger('vist-verification')
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler('vist-verification.log')
        fh.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
