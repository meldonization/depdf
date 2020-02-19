from decimal import Decimal
from statistics import mean

from pdfplumber.page import Page

from depdf.base import Base
from depdf.components import Paragraph, Table
from depdf.config import check_config, check_config_type
from depdf.error import PageTypeError
from depdf.log import logger_init
from depdf.page_tools import remove_duplicate_chars, analysis_char_size, analysis_page_orientation
from depdf.page_tools import PAGE_PORTRAIT
from depdf.settings import DEFAULT_CHAR_SIZE

log = logger_init(__name__)


class DePage(Base):
    _cached_properties = Base._cached_properties + [
        '_screenshot', '_objects', '_border', '_phrases'
    ]

    # 一般而言 下一页的 new_para_start_flag = False 并且
    # 上一页的 new_para_end_flag = False 表示跨页面段落出现
    new_para_start_flag = True  # 该页面起始段落为新段落（第一行左边界是否有缩进）
    new_para_end_flag = True  # 该页面最后一个段落是否标志为新段落（最后一行右边界是否有缩进）

    orientation = PAGE_PORTRAIT  # page orientation 'portrait' or 'landscape'
    ave_cs = DEFAULT_CHAR_SIZE  # average char size
    min_cs = DEFAULT_CHAR_SIZE  # minimum char size
    y_tolerance = 3  # y_tolerance in pdfplumber within words extraction
    pagination = None  # 页面底部的页码信息
    phrases = None  # 页面内的语句
    frame_top = 0
    ave_lh = 3

    @check_config
    def __init__(self, page, pid=1, same=None, logo=None, config=None):
        """
        :param page: pdfplumber page object
        :param pid: page number start from 1
        :param same: header & footer
        :param logo: watermark and logo
        :param config: depdf config
        """
        check_page_type(page)
        self._page = page
        self._pid = int(pid)
        check_config_type(config)
        self._config = config
        self.same = same or []
        self.logo = logo or []
        self.frame_bottom = self.width

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        check_config_type(value)
        self.refresh()
        self._config = value

    @property
    def pid(self):
        return self._pid

    @pid.setter
    def pid(self, value):
        self.refresh()
        self._pid = int(value)

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        check_page_type(value)
        self.refresh()
        self._page = value

    @property
    def width(self):
        return self.page.width

    @property
    def height(self):
        return self.page.height

    def to_screenshot(self):
        res = getattr(self.config, 'resolution')
        return self.page.to_image(resolution=res)

    @property
    def screenshot(self):
        screenshot = self._get_cached_property('_screenshot', self.to_screenshot)
        return screenshot.original

    @property
    def chars(self):
        return self.page.chars

    @property
    def border(self):
        return self._get_cached_property('_border', self.analysis_paragraph_border)

    @property
    def objects(self):
        object_list = self.process_page()
        return object_list

    @property
    def paragraphs(self):
        paragraph_list = [i for i in self.objects if isinstance(i, Paragraph)]
        return paragraph_list

    @property
    def tables(self):
        table_list = [i for i in self.objects if isinstance(i, Table)]
        return table_list

    @property
    def to_html(self):
        # todo
        html = ''
        self.html = html
        return html

    def process_page(self):
        # 预处理页面
        self.pre_process()
        # 分析页面内的主要区域
        self.analysis_main_frame()
        # 分析页面内线段
        self.analysis_lines()
        # 分析页面段落边界
        self.analysis_paragraph_border()
        # 解析页面内的 objects
        object_list = []
        return object_list

    def pre_process(self):
        overlap_size = getattr(self.config, 'char_overlap_size')
        remove_duplicate_chars(self.page.chars, overlap_size=overlap_size)
        self.analysis_page_attributes()

    def analysis_page_attributes(self):
        # average char size within the page
        dcs = getattr(self.config, 'default_char_size')
        csu = getattr(self.config, 'char_size_upper')
        csl = getattr(self.config, 'char_size_lower')
        self.ave_cs, self.min_cs = analysis_char_size(self.page.chars, char_size_upper=csu,
                                                      char_size_lower=csl, default_char_size=dcs)
        self.orientation = analysis_page_orientation(self.page)
        y_tolerance = 3 if self.ave_cs / 3 <= 3 else self.ave_cs / 2
        cyt = getattr(self.config, 'y_tolerance')
        self.y_tolerance = Decimal(cyt) if cyt is not None else y_tolerance

    def analysis_main_frame(self):
        mft = getattr(self.config, 'main_frame_tolerance')
        # top_line's bottoms
        tl_bs = [i['bottom'] + mft for i in self.same if i['mode'] == self.orientation and i['level'] == 'head']
        # bottom_line's tops
        bl_ts = [i['top'] for i in self.same if i['mode'] == self.orientation and i['level'] == 'tail']
        self.frame_top = max(tl_bs) if tl_bs else 0
        self.frame_bottom = min(bl_ts) if bl_ts else self.height
        self.extract_main_phrases()

    def extract_main_phrases(self):
        words = [
            i for i in self.page.extract_words(x_tolerance=self.ave_cs * 3 / 2, y_tolerance=self.y_tolerance)
            if 'top' in i and i['top'] >= self.frame_top and 'bottom' in i and i['bottom'] <= self.frame_bottom
        ]
        line_heights = list(
            filter(lambda x: x > 0, [words[i + 1]['top'] - words[i]['bottom'] for i in range(len(words) - 1)])
        )
        # 平均行高
        self.ave_lh = mean(line_heights) if line_heights else self.ave_cs / 2

    def analysis_paragraph_border(self):
        # todo
        pass

    def analysis_lines(self):
        # todo
        pass


def check_page_type(page):
    if not isinstance(page, Page):
        raise PageTypeError(page)
