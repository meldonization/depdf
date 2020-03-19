from depdf.base import Base, Box
from depdf.config import check_config
from depdf.log import logger_init

log = logger_init(__name__)


class Image(Base, Box):
    object_type = 'image'

    @check_config
    def __init__(self, bbox=None, src='', percent=100, pid='1', img_idx=1, scan=False, config=None):
        self.bbox = bbox
        self.scan = scan
        self.src = src
        self.img_idx = img_idx
        self.pid = pid
        img_id = 'page-{pid}-image-{img_idx}'.format(pid=pid, img_idx=img_idx)
        img_class = '{img_class} page-{pid}'.format(img_class=getattr(config, 'image_class'), pid=pid)
        html = '<img id="{img_id}" class="{img_class}" src="{src}" width="{percent}%">'.format(
            img_id=img_id, img_class=img_class, src=src, percent=min(round(percent), 100)
        )
        html += '</img>'
        self.html = html

    def __repr__(self):
        scan_flag = '[scan]' if self.scan else ''
        return '<depdf.Image{}: ({}, {}) -> {}>'.format(scan_flag, self.pid, self.img_idx, self.src)
