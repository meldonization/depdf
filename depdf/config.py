import uuid
from .utils import logger_init
from .base import Base

log = logger_init('depdf:config')

DEFAULT_TABLE_FLAG = True
DEFAULT_PARAGRAPH_FLAG = True
DEFAULT_IMG_FLAG = False
DEFAULT_DEBUG_FLAG = False
DEFAULT_ADD_LINE_FLAG = False
DEFAULT_SNAP_FLAG = False
DEFAULT_LOGO_FLAG = True
DEFAULT_HEADER_FOOTER_FLAG = True
DEFAULT_RESOLUTION = 144
DEFAULT_DOUBLE_LINE_TOLERANCE = 3


class Config(Base):
    table_flag = DEFAULT_TABLE_FLAG
    paragraph_flag = DEFAULT_PARAGRAPH_FLAG
    img_flag = DEFAULT_IMG_FLAG
    debug_flag = DEFAULT_DEBUG_FLAG
    add_line_flag = DEFAULT_ADD_LINE_FLAG
    snap_flag = DEFAULT_SNAP_FLAG
    logo_flag = DEFAULT_LOGO_FLAG
    header_footer_flag = DEFAULT_HEADER_FOOTER_FLAG
    resolution = DEFAULT_RESOLUTION
    double_line_tolerance = DEFAULT_DOUBLE_LINE_TOLERANCE

    def __init__(self, **kwargs):
        self.unique_prefix = uuid.uuid4()
        for key, value in kwargs.items():
            setattr(self, key, value)
            if not hasattr(self, key):
                log.warning('config attributes not found: {}'.format(key))

    @property
    def to_json(self):
        return {
            i: getattr(self, i, None)
            for i in dir(self)
            if not i.startswith('__')
        }
