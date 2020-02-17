import uuid
from functools import wraps

from depdf.base import Base
from depdf.error import ConfigTypeError
from depdf.log import logger_init
from depdf.settings import *

log = logger_init(__name__)


class Config(Base):
    # page
    table_flag = DEFAULT_TABLE_FLAG
    paragraph_flag = DEFAULT_PARAGRAPH_FLAG
    img_flag = DEFAULT_IMG_FLAG
    logo_flag = DEFAULT_LOGO_FLAG
    header_footer_flag = DEFAULT_HEADER_FOOTER_FLAG
    resolution = DEFAULT_RESOLUTION

    # table
    snap_flag = DEFAULT_SNAP_FLAG
    add_line_flag = DEFAULT_ADD_LINE_FLAG
    double_line_tolerance = DEFAULT_DOUBLE_LINE_TOLERANCE
    table_cell_merge_tolerance = DEFAULT_TABLE_CELL_MERGE_TOLERANCE
    skip_empty_table = DEFAULT_SKIP_EMPTY_TABLE

    # head & tail
    default_head_tail_page_offset_percent = DEFAULT_HEAD_TAIL_PAGE_OFFSET_PERCENT

    # log
    log_level = DEFAULT_LOG_LEVEL
    verbose_flag = DEFAULT_VERBOSE_FLAG
    debug_flag = DEFAULT_DEBUG_FLAG

    # paragraph
    span_class = DEFAULT_SPAN_CLASS
    paragraph_class = DEFAULT_PARAGRAPH_CLASS
    table_class = DEFAULT_TABLE_CLASS

    def __init__(self, **kwargs):
        # add unique prefix to dePDF instance
        self.unique_prefix = uuid.uuid4()

        if kwargs.get('debug_flag'):
            self.log_level = logging.DEBUG

        # add configuration parameters
        self.update(**kwargs)

        # set logging level by log_level parameter
        logging.getLogger('depdf').setLevel(self.log_level)

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                log.warning('config attributes not found: {}'.format(key))


DEFAULT_CONFIG = Config()
PDF_IMAGE_KEYS = ['srcsize', 'height', 'width', 'bits']
DEFAULT_CONFIG_KEYS = list(DEFAULT_CONFIG.to_dict.keys())


def check_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        config = kwargs.get('config')
        if config is None:
            config = DEFAULT_CONFIG
        elif not isinstance(config, Config):
            raise ConfigTypeError(config)
        kwargs['config'] = config
        return func(*args, **kwargs)
    return wrapper
