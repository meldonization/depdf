from decimal import Decimal
import logging

# general pdf config
DEFAULT_LOGO_FLAG = True
DEFAULT_HEADER_FOOTER_FLAG = True
DEFAULT_TEMP_DIR_PREFIX = 'temp_depdf'

# general page extraction config
DEFAULT_TABLE_FLAG = True
DEFAULT_PARAGRAPH_FLAG = True
DEFAULT_IMAGE_FLAG = True
DEFAULT_RESOLUTION = 144
DEFAULT_PAGE_NUM_TOP_FRACTION = Decimal('0.75')
DEFAULT_PAGE_NUM_LEFT_FRACTION = Decimal('0.44')
DEFAULT_PAGE_NUM_RIGHT_FRACTION = Decimal('0.56')

# multiple column mini page config
DEFAULT_MULTIPLE_COLUMNS_FLAG = True
DEFAULT_MAX_COLUMNS = 3
DEFAULT_COLUMN_REGION_HALF_WIDTH = 4
DEFAULT_MIN_COLUMN_REGION_OBJECTS = 1

# char
DEFAULT_CHAR_OVERLAP_SIZE = 3  # => depdf.page_tools.remove_duplicate_chars
DEFAULT_CHAR_SIZE = Decimal('12')  # => depdf.page_tools.calculate_average_char_size
DEFAULT_CHAR_SIZE_UPPER = Decimal('30')  # => depdf.page_tools.calculate_average_char_size
DEFAULT_CHAR_SIZE_LOWER = Decimal('3')  # => depdf.page_tools.calculate_average_char_size

# table extraction config
DEFAULT_TABLE_CELL_MERGE_TOLERANCE = 5
DEFAULT_ADD_LINE_FLAG = False
DEFAULT_SNAP_FLAG = False
DEFAULT_MAX_DOUBLE_LINE_TOLERANCE = 3  # => depdf.page_tools.remove_single_lines
DEFAULT_MIN_DOUBLE_LINE_TOLERANCE = Decimal('0.05')  # => depdf.page_tools.remove_single_lines
DEFAULT_VERTICAL_DOUBLE_LINE_TOLERANCE = Decimal('2')  # => depdf.page_tools.remove_single_lines
DEFAULT_SKIP_EMPTY_TABLE = False
DEFAULT_ADD_VERTICAL_LINES_FLAG = False  # 是否为表格自动增加可能缺失的竖线
DEFAULT_ADD_HORIZONTAL_LINES_FLAG = False  # 是否为表格自动增加可能缺失的横线
DEFAULT_ADD_HORIZONTAL_LINE_TOLERANCE = Decimal('0.1')  # 增加表格顶部和底部的横线的参数

# image
DEFAULT_MIN_IMAGE_SIZE = 80  # minimum width or height of image which to be ignored
DEFAULT_IMAGE_RESOLUTION = 300

# head & tail extraction
DEFAULT_HEAD_TAIL_PAGE_OFFSET_PERCENT = 0.1  # head/tail max-height percent form top & bottom of page

# depdf logging setting
DEFAULT_LOG_FORMAT = '%(levelname)s:%(name)s:%(asctime)-15s %(message)s'
DEFAULT_LOG_FMT = '%Y-%m-%dT%H:%M:%S'
DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_VERBOSE_FLAG = False
DEFAULT_DEBUG_FLAG = False

# html config
DEFAULT_HTML_PARSER = 'html.parser'
DEFAULT_SPAN_CLASS = 'pdf-span'
DEFAULT_PARAGRAPH_CLASS = 'pdf-paragraph'
DEFAULT_TABLE_CLASS = 'pdf-table'
DEFAULT_PDF_CLASS = 'pdf-content'
DEFAULT_IMAGE_CLASS = 'pdf-image'
DEFAULT_PAGE_CLASS = 'pdf-page'
DEFAULT_MINI_PAGE_CLASS = 'pdf-mini-page'
