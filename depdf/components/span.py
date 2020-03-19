from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init
from depdf.utils import construct_style, repr_str

log = logger_init(__name__)


class Span(Base, Box):
    object_type = 'span'

    @check_config
    def __init__(self, bbox=None, span_text='', config=None, style=None):
        self.bbox = bbox
        self.text = span_text
        span_class = getattr(config, 'span_class')
        style_text = construct_style(style=style)
        self.html = '<span class="{span_class}"{style_text}>{span_text}</span>'.format(
            span_class=span_class, span_text=span_text, style_text=style_text
        )

    def __repr__(self):
        return '<depdf.Span: {}>'.format(repr_str(self.text))
