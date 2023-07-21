# setup simple console logger
import logging

logger_cache = {}


def get_logger(name: str) -> logging.Logger:
    log = logger_cache.get(name, None)
    if log is not None:
        return log

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(module)s | %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    file_handler = logging.FileHandler(f'{name}-log.txt')
    file_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    logger.addHandler(file_handler)

    logger_cache[name] = logger

    return logger
