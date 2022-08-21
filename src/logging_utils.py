import logging
from logging import Logger


def get_logger(name: str) -> Logger:
    formatter = logging.Formatter('%(name)s %(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    return logger
