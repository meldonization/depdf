import os
from statistics import mean, median
import uuid

from pdfplumber.page import Page

from depdf.base import Base
from depdf.components import Image, Paragraph
from depdf.config import check_config, check_config_type
from depdf.error import PageTypeError
from depdf.page_tools import *

log = logger_init(__name__)


class DePage(Base):
    _cached_properties = Base._cached_properties + ['_screenshot', '_objects']

    # 一般而言 下一页的 new_para_start_flag = False 并且
    # 上一页的 new_para_end_flag = False 表示跨页面段落出现
    new_para_start_flag = True  # 该页面起始段落为新段落（第一行左边界是否有缩进）
    new_para_end_flag = True  # 该页面最后一个段落是否标志为新段落（最后一行右边界是否有缩进）

    # 这些变量会在后续处理页面时再次更新
    orientation = ''  # page orientation 'portrait' or 'landscape'
    ave_cs = 0  # average char size
    min_cs = 0  # minimum char size
    x_tolerance = 3  # x_tolerance in pdfplumber during words extraction
    y_tolerance = 3  # y_tolerance in pdfplumber during words extraction
    page_word = None  # 页面底部的页码信息
    phrases = None  # 页面内的语句相当于 words
    frame_top = 0  # 除去页眉页脚后的页面上边界
    frame_bottom = 0  # 除去页眉页脚后的页面下边界
    ave_lh = 3  # 平均行高
    border = (0, 0, 0, 0)  # 页面内段落区域的边界，相当于 bbox
    v_edges = []  # 表格竖线
    h_edges = []  # 表格横线
    verbose = False
    debug = False
    temp_dir = 'temp'
    prefix = uuid.uuid4()
    _tables = []
    _tables_raw = []
    _paragraphs = []
    _images = []
    _images_raw = []
    object_key_list = ['_tables', '_paragraphs', '_images']
    toc_flag = False

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
        self.border = (0, self.width, 0, self.height)
        self.set_global()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        check_config_type(value)
        self._config = value
        self.refresh()

    def set_global(self):
        prefix = getattr(self.config, 'unique_prefix')
        if prefix:
            self.prefix = getattr(self.config, 'unique_prefix')
        temp = getattr(self.config, 'temp_dir_prefix')
        if temp:
            self.temp_dir = getattr(self.config, 'temp_dir_prefix')
        self.verbose = getattr(self.config, 'verbose_flag')
        self.debug = getattr(self.config, 'debug_flag')

    def refresh(self):
        self.set_global()
        return super().refresh()

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
    def objects(self):
        object_list = self._get_cached_property('_objects', self.process_page)
        return object_list

    @property
    def paragraphs(self):
        return self._paragraphs

    @property
    def tables(self):
        return self._tables

    @property
    def tables_raw(self):
        return self._tables_raw

    @property
    def images(self):
        return self._images

    @property
    def images_raw(self):
        return self._images_raw

    @property
    def to_html(self):
        # todo
        html = ''
        self.html = html
        return html

    def process_page(self):
        if self.verbose:
            log.info('Processing {0} page {1}'.format(self.prefix, self.pid))
        # 预处理页面
        #  - [1] 删除重叠的字符
        overlap_size = getattr(self.config, 'char_overlap_size')
        remove_duplicate_chars(self.page.chars, overlap_size=overlap_size)

        # 分析页面的字符元素
        #  - [2] 分析页面内字符的基本信息
        self.analyze_page_attributes()
        #  - [3] 分析页面的正文主要区域
        self.analyze_main_frame()
        #  - [4] 分析页面内的短语和行
        self.extract_phrases()

        # 解析页面内的 objects[表格 + 段落]
        #  - [5] 分析页面内的线段
        if getattr(self.config, 'table_flag'):
            self.analyze_lines()
        #  - [6] 获取页面内表格
            self.extract_tables()
        #  - [7] 获取页面内图像
        if getattr(self.config, 'image_flag'):
            self.extract_images()
        if getattr(self.config, 'paragraph_flag'):
            #  - [8] 分析页面段落边界
            self.analyze_paragraph_border()
            #  - [9] 获取页面内的段落
            self.extract_paragraph()

        # 集合页面内的所有 objects
        object_list = []
        for key in self.object_key_list:
            object_list.extend(getattr(self, key, []))
        return sorted(object_list, key=lambda x: x.bbox[1])

    def check_if_toc_page(self):
        all_text = self.page.extract_text()
        all_text_line = all_text.split('\n') if all_text else []
        lines = [i.replace(' ', '') for i in all_text_line]
        if re.findall('目录', ''.join(''.join(lines).split())):
            for line in lines:
                toc_tmp = TOC_LINE_RE.findall(line.replace('\xa0', ''))
                if toc_tmp and toc_tmp[0] and not toc_tmp[0][-1].isdigit():
                    self.toc_flag = True
                    break

    def analyze_page_attributes(self):
        # average char size within the page
        dcs = getattr(self.config, 'default_char_size')
        csu = getattr(self.config, 'char_size_upper')
        csl = getattr(self.config, 'char_size_lower')
        self.ave_cs, self.min_cs = analyze_char_size(self.page.chars, char_size_upper=csu,
                                                     char_size_lower=csl, default_char_size=dcs)
        self.orientation = analyze_page_orientation(self.page)
        y_tolerance = 3 if self.ave_cs / 3 <= 3 else self.ave_cs / 2
        cyt = getattr(self.config, 'y_tolerance')
        self.y_tolerance = Decimal(cyt) if cyt is not None else y_tolerance
        cxt = getattr(self.config, 'x_tolerance')
        self.x_tolerance = Decimal(cxt) if cxt is not None else self.ave_cs * 3 / 2

    def analyze_main_frame(self):
        mft = getattr(self.config, 'main_frame_tolerance')
        if mft is None:
            mft = Decimal(self.ave_cs / 2)
        # top_line's bottoms
        tl_bs = [i['bottom'] + mft for i in self.same if i['mode'] == self.orientation and i['level'] == 'head']
        # bottom_line's tops
        bl_ts = [i['top'] for i in self.same if i['mode'] == self.orientation and i['level'] == 'tail']
        self.frame_top = max(tl_bs) if tl_bs else 0
        self.frame_bottom = min(bl_ts) if bl_ts else self.height

    def extract_phrases(self):
        phrases = [
            i for i in self.page.extract_words(x_tolerance=self.x_tolerance, y_tolerance=self.y_tolerance)
            if 'top' in i and i['top'] >= self.frame_top and 'bottom' in i and i['bottom'] <= self.frame_bottom
        ]
        self.phrases = phrases
        line_heights = list(
            filter(lambda x: x > 0, [phrases[i + 1]['top'] - phrases[i]['bottom'] for i in range(len(phrases) - 1)])
        )
        # 平均行高
        self.ave_lh = mean(line_heights) if line_heights else self.ave_cs / 2
        # 页面底部的页码行
        pn_tf = getattr(self.config, 'page_num_top_fraction')
        pn_lf = getattr(self.config, 'page_num_left_fraction')
        pn_rf = getattr(self.config, 'page_num_right_fraction')
        self.page_word = analyze_page_num_word(phrases, self.height, self.width, top_fraction=pn_tf,
                                               left_fraction=pn_lf, right_fraction=pn_rf)
        # normalize page word boundary (EN/NUM chars are taller and slimmer than CN chars)
        for w in self.phrases:
            try:
                bbox = (w['x0'], w['top'], w['x1'], w['bottom'])
                c = self.page.crop(bbox)
                top = median([j['top'] for j in c.chars])
                bottom = median([j['bottom'] for j in c.chars])
                w['top'], w['bottom'] = top, bottom
            except:
                pass
        if self.debug:
            page_image = self.screenshot
            page_image.draw_rects(self.phrases)
            img_file = os.path.join(self.temp_dir, self.prefix + '_text_border_{0}.png'.format(self.pid))
            page_image.save(img_file, format="PNG")

    def analyze_lines(self):
        rect_edges_raw = self.page.edges
        try:
            rect_edges_raw = self.page.within_bbox((1, 1, self.width - 1, self.height - 1)).edges
        except Exception as e:
            if self.verbose:
                log.error('analyze_lines error: {}'.format(e))
        h_lines, v_lines = edges_to_lines(rect_edges_raw)

        # 去除特别细的单线（干扰线）
        v_dlt = getattr(self.config, 'vertical_double_line_tolerance')
        max_dlt = getattr(self.config, 'max_double_line_tolerance')
        min_dlt = getattr(self.config, 'min_double_line_tolerance')
        h_lines = remove_single_lines(h_lines, max_double=max_dlt, min_double=min_dlt, vertical_double=v_dlt)
        v_lines = remove_single_lines(v_lines, max_double=max_dlt, min_double=min_dlt, vertical_double=v_dlt, m='v')

        # 有些时候表格会隐藏在 pdf_page.lines 中，比如虚线
        if getattr(self.config, 'dotted_line_flag'):
            page_lines = self.page.lines
            h_lines.extend([i for i in page_lines if i['height'] == 0])
            v_lines.extend([i for i in page_lines if i['width'] == 0])

        # 有些表格的边框是曲线
        curved_line_flag = getattr(self.config, 'curved_line_flag')
        page_curves = self.page.curves if curved_line_flag else []
        h_curves, v_curves = curve_to_lines(page_curves)
        h_lines.extend(h_curves)
        v_lines.extend(v_curves)

        # 设定页面的横竖线列表
        self.h_edges = [{'top': i['top'], 'x0': i['x0'], 'x1': i['x1']} for i in h_lines]
        self.v_edges = [{'x': i['x0'], 'top': i['top'], 'bottom': i['bottom']} for i in v_lines]

        if self.debug:
            page_image = self.screenshot
            page_image.draw_lines(h_lines)
            img_file = os.path.join(self.temp_dir, self.prefix + '_table_cell_border_h_clean_{0}.png'.format(self.pid))
            page_image.save(img_file, format="PNG")
            page_image.reset()
            page_image.draw_lines(v_lines)
            img_file = os.path.join(self.temp_dir, self.prefix + '_table_cell_border_v_clean_{0}.png'.format(self.pid))
            page_image.save(img_file, format="PNG")

    def extract_tables(self):
        table_params = {
            'vertical_strategy': 'explicit',
            'horizontal_strategy': 'explicit',
            'explicit_vertical_lines': self.v_edges,
            'explicit_horizontal_lines': self.h_edges,
            'edge_min_length': self.ave_cs,
            'join_tolerance': self.ave_cs,
            'intersection_tolerance': self.ave_cs,
        }
        tables_raw = sorted(self.page.find_tables(table_settings=table_params), key=lambda x: x.bbox[1])
        self._tables_raw = tables_raw
        if self.debug and tables_raw:
            page_image = self.screenshot
            for i in tables_raw:
                page_image.draw_rects(i.cells)
            img_file = os.path.join(self.temp_dir, self.prefix + '_table_cell_border_{0}.png'.format(self.pid))
            page_image.save(img_file, format="PNG")
        table_clean = [
            convert_plumber_table(self.page, table, pid=self.pid, tid=tid + 1, config=self.config,
                                  min_cs=self.min_cs, ave_cs=self.ave_cs)
            for tid, table in enumerate(tables_raw)
        ]
        self._tables = [i for i in table_clean if i is not None]
        if self.verbose:
            log.info('{0} / page-{1} tables count: {2}'.format(self.prefix, self.pid, len(self._tables)))

    def extract_images(self):
        images_raw = merge_page_figures(self.page, tables_raw=self._tables_raw,
                                        logo=self.logo, pid=self.pid)
        self._images_raw = images_raw
        if self.verbose:
            log.info('{0} / page-{1} figure count: {2}'.format(self.prefix, self.pid, len(images_raw)))

        mis = getattr(self.config, 'min_image_size')
        res = getattr(self.config, 'resolution')
        images = []
        for fid, i in enumerate(images_raw):
            if i['height'] <= mis or i['width'] <= mis:
                continue
            img_file = os.path.join(self.temp_dir, self.prefix + '_{0}_image_{1}.png'.format(self.pid, fid + 1))
            bbox = (i['x0'], i['top'], i['x1'], i['bottom'])
            image = self.page.within_bbox(bbox)
            pic = image.to_image(resolution=res)
            pic.save(img_file, format='PNG')
            scan = i['width'] * i['height'] / self.width / self.height >= 0.7
            image = Image(bbox=bbox, src=img_file, pid=self.pid, img_idx=fid + 1, config=self.config, scan=scan)
            images.append(image)
        self._images = images
        if self.debug and images_raw:
            page_image = self.screenshot
            page_image.draw_rects(self.page.figures)
            image_file = os.path.join(self.temp_dir, self.prefix + '_image_border_{0}.png'.format(self.pid))
            page_image.save(image_file, format="PNG")

    def analyze_paragraph_border(self):
        border = calculate_paragraph_border(self)
        self.border = border
        if self.debug:
            page_image = self.screenshot
            page_image.draw_rects([border])
            img_file = os.path.join(self.temp_dir, self.prefix + '_paragraph_border_{0}.png'.format(self.pid))
            page_image.save(img_file, format="PNG")

    def extract_paragraph(self):
        # todo  (ll, tt, lr, tb)
        para_idx = 1
        previous_top = previous_bottom = self.border[1]
        previous_right = self.border[0]
        new_para = None
        for phrase in self.phrases:
            pass


def check_page_type(page):
    if not isinstance(page, Page):
        raise PageTypeError(page)
