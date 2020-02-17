import logging

# general page extraction config
DEFAULT_TABLE_FLAG = True
DEFAULT_PARAGRAPH_FLAG = True
DEFAULT_IMG_FLAG = False
DEFAULT_LOGO_FLAG = True
DEFAULT_HEADER_FOOTER_FLAG = True
DEFAULT_RESOLUTION = 144

# table extraction config
DEFAULT_TABLE_CELL_MERGE_TOLERANCE = 5
DEFAULT_ADD_LINE_FLAG = False
DEFAULT_SNAP_FLAG = False
DEFAULT_DOUBLE_LINE_TOLERANCE = 3
DEFAULT_SKIP_EMPTY_TABLE = False

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
