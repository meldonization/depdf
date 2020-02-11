from depdf.settings import *


def logger_init(name):
    logging.basicConfig(level=DEFAULT_LOG_LEVEL, format=DEFAULT_LOG_FORMAT, datefmt=DEFAULT_LOG_FMT)
    logger = logging.getLogger(name)
    return logger
