from functools import wraps
import os

from depdf.error import ConfigTypeError
from depdf.log import logger_init
from depdf.settings import *

log = logger_init(__name__)


class Config(object):
    # pdf
    logo_flag = DEFAULT_LOGO_FLAG
    header_footer_flag = DEFAULT_HEADER_FOOTER_FLAG
    temp_dir_prefix = DEFAULT_TEMP_DIR_PREFIX
    unique_prefix = None  # 该参数会根据 pdf 的文件名自动更新

    # page
    table_flag = DEFAULT_TABLE_FLAG
    paragraph_flag = DEFAULT_PARAGRAPH_FLAG
    image_flag = DEFAULT_IMAGE_FLAG
    resolution = DEFAULT_RESOLUTION
    main_frame_tolerance = None  # 该参数可通过页面内容自动分析
    x_tolerance = None  # 该参数可通过页面内容自动分析
    y_tolerance = None  # 该参数可通过页面内容自动分析
    page_num_top_fraction = DEFAULT_PAGE_NUM_TOP_FRACTION
    page_num_left_fraction = DEFAULT_PAGE_NUM_LEFT_FRACTION
    page_num_right_fraction = DEFAULT_PAGE_NUM_RIGHT_FRACTION
    dotted_line_flag = True
    curved_line_flag = False

    # mini page
    multiple_columns_flag = DEFAULT_MULTIPLE_COLUMNS_FLAG
    max_columns = DEFAULT_MAX_COLUMNS
    column_region_half_width = DEFAULT_COLUMN_REGION_HALF_WIDTH
    min_column_region_objects = DEFAULT_MIN_COLUMN_REGION_OBJECTS

    # chars
    char_overlap_size = DEFAULT_CHAR_OVERLAP_SIZE
    default_char_size = DEFAULT_CHAR_SIZE
    char_size_upper = DEFAULT_CHAR_SIZE_UPPER
    char_size_lower = DEFAULT_CHAR_SIZE_LOWER

    # table
    snap_flag = DEFAULT_SNAP_FLAG
    add_line_flag = DEFAULT_ADD_LINE_FLAG
    min_double_line_tolerance = DEFAULT_MIN_DOUBLE_LINE_TOLERANCE  # used in page class
    max_double_line_tolerance = DEFAULT_MAX_DOUBLE_LINE_TOLERANCE  # used in page class
    vertical_double_line_tolerance = DEFAULT_VERTICAL_DOUBLE_LINE_TOLERANCE  # used in page class
    table_cell_merge_tolerance = DEFAULT_TABLE_CELL_MERGE_TOLERANCE
    skip_empty_table = DEFAULT_SKIP_EMPTY_TABLE
    add_vertical_lines_flag = DEFAULT_ADD_VERTICAL_LINES_FLAG
    add_horizontal_lines_flag = DEFAULT_ADD_HORIZONTAL_LINES_FLAG
    add_horizontal_line_tolerance = DEFAULT_ADD_HORIZONTAL_LINE_TOLERANCE

    # image
    min_image_size = DEFAULT_MIN_IMAGE_SIZE
    image_resolution = DEFAULT_IMAGE_RESOLUTION

    # head & tail
    default_head_tail_page_offset_percent = DEFAULT_HEAD_TAIL_PAGE_OFFSET_PERCENT

    # log
    log_level = DEFAULT_LOG_LEVEL
    verbose_flag = DEFAULT_VERBOSE_FLAG
    debug_flag = DEFAULT_DEBUG_FLAG

    # html
    span_class = DEFAULT_SPAN_CLASS
    paragraph_class = DEFAULT_PARAGRAPH_CLASS
    table_class = DEFAULT_TABLE_CLASS
    pdf_class = DEFAULT_PDF_CLASS
    image_class = DEFAULT_IMAGE_CLASS
    page_class = DEFAULT_PAGE_CLASS
    mini_page_class = DEFAULT_MINI_PAGE_CLASS

    def __init__(self, **kwargs):
        # set log level automatically if debug mode enabled
        if kwargs.get('debug_flag'):
            self.log_level = logging.DEBUG
        if kwargs.get('verbose_flag'):
            self.log_level = logging.INFO

        # add configuration parameters
        self.update(**kwargs)
        self._kwargs = kwargs

        # create temporary folder
        if not os.path.isdir(self.temp_dir_prefix):
            os.mkdir(self.temp_dir_prefix)

        # set logging level by log_level parameter
        logging.getLogger('depdf').setLevel(self.log_level)

    def __repr__(self):
        return '<depdf.Config: {}>'.format(self._kwargs)

    @property
    def to_dict(self):
        return {
            i: getattr(self, i, None) for i in dir(self)
            if not i.startswith('_') and i not in ['to_dict', 'copy', 'update']
        }

    def copy(self, **kwargs):
        copied_config = Config(**self.to_dict)
        copied_config.update(**kwargs)
        return copied_config

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
        else:
            check_config_type(config)
        kwargs['config'] = config
        return func(*args, **kwargs)
    return wrapper


def check_config_type(config):
    if not isinstance(config, Config):
        raise ConfigTypeError(config)
