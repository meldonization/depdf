from depdf.base import Base
from depdf.config import check_config
from depdf.log import logger_init
from depdf.components.paragraph import Paragraph
from depdf.components.span import Span
from depdf.components.table import Table

log = logger_init(__name__)


class Page(Base):

    @check_config
    def __init__(self, pdf, pid=1):
        # todo
        self.pid = pid
