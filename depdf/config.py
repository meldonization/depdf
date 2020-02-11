import uuid
from functools import wraps

from depdf.base import Base
from depdf.log import logger_init
from depdf.settings import *

log = logger_init(__name__)


class Config(Base):
    table_flag = DEFAULT_TABLE_FLAG
    paragraph_flag = DEFAULT_PARAGRAPH_FLAG
    img_flag = DEFAULT_IMG_FLAG
    debug_flag = DEFAULT_DEBUG_FLAG
    logo_flag = DEFAULT_LOGO_FLAG
    header_footer_flag = DEFAULT_HEADER_FOOTER_FLAG
    resolution = DEFAULT_RESOLUTION

    snap_flag = DEFAULT_SNAP_FLAG
    add_line_flag = DEFAULT_ADD_LINE_FLAG
    double_line_tolerance = DEFAULT_DOUBLE_LINE_TOLERANCE
    table_cell_merge_tolerance = DEFAULT_TABLE_CELL_MERGE_TOLERANCE
    skip_empty_table = DEFAULT_SKIP_EMPTY_TABLE

    log_level = DEFAULT_LOG_LEVEL

    span_class = DEFAULT_SPAN_CLASS
    paragraph_class = DEFAULT_PARAGRAPH_CLASS
    table_class = DEFAULT_TABLE_CLASS

    def __init__(self, **kwargs):
        # add unique prefix to dePDF instance
        self.unique_prefix = uuid.uuid4()

        # add configuration parameters
        for key, value in kwargs.items():
            setattr(self, key, value)
            if not hasattr(self, key):
                log.warning('config attributes not found: {}'.format(key))

        # set logging level by log_level parameter
        logging.getLogger('depdf').setLevel(self.log_level)


DEFAULT_CONFIG = Config()


def check_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = kwargs.get('config')
        if not isinstance(config, Config):
            config = DEFAULT_CONFIG
        return func(*args, config=config, **kwargs)
    return wrapper
