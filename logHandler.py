import logging

general_logger = 'vist-verification'

def initialize():
    logger = logging.getLogger(general_logger)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler('vist-verification.log')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
