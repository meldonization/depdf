from depdf.base import Box, InnerWrapper
from depdf.config import check_config
from depdf.log import logger_init
from depdf.utils import calc_bbox, construct_style

log = logger_init(__name__)


class Paragraph(InnerWrapper, Box):
    object_type = 'paragraph'

    @check_config
    def __init__(self, bbox=None, text='', pid=1, para_idx=1, config=None, inner_objects=None, style=None):
        para_id = 'page-{pid}-paragraph-{para_id}'.format(pid=pid, para_id=para_idx)
        para_class = '{para_class} page-{pid}'.format(para_class=getattr(config, 'paragraph_class'), pid=pid)
        style = construct_style(style=style)
        html = '<p id="{para_id}" class="{para_class}"{style}>'.format(
            para_id=para_id, para_class=para_class, style=style
        )
        self.pid = pid
        self.para_id = para_idx
        self.bbox = bbox
        if text:
            self.text = text
            html += str(text)
        else:
            if bbox is None:
                self.bbox = calc_bbox(inner_objects)
            self._inner_objects = inner_objects
            for obj in inner_objects:
                html += getattr(obj, 'html', '')
        html += '</p>'
        self.html = html

    def __repr__(self):
        return '<depdf.Paragraph: ({}, {})>'.format(self.pid, self.para_id)
