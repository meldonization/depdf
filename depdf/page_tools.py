from collections import Counter
from decimal import Decimal
import re

from depdf.components import Table, Cell
from depdf.config import PDF_IMAGE_KEYS
from depdf.log import logger_init

log = logger_init(__name__)
PAGE_PORTRAIT = 'portrait'
PAGE_LANDSCAPE = 'landscape'
NUM_SYMBOLS = '0-9lxvi'  # 页码的可能数字
PAGE_NUM_RE = re.compile((
    r"^[-－]*[{0}]+(?:[-－]+[{0}]+)*[-－]*$|^[-－]+[{0}]+[-－]+$|"
    r"^[-－]*[{0}]+[-－]*$|^[{0}]+(?:-[{0}]+)*[-－]+[{0}]+$"
).format(NUM_SYMBOLS), re.I)  # 1-1-1 or 11 or -1- or iv or 1-1-XVI

TOC_SYMBOLS = '.…·'  # add to toc symbol list if new separator is found
TOC_OCCURRENCE = '+'
TOC_LINE_RE = re.compile(r"^(.*?)[{}]{}[-－]*[0-9]+[-－]*$".format(TOC_SYMBOLS, TOC_OCCURRENCE))


def remove_duplicate_chars(chars, overlap_size=3):
    # 去除通过叠加字符来实现加粗的多余字符
    delete_index_list = []
    for char_index, char in enumerate(chars):
        for i in reversed(range(char_index)):
            tmp_char = chars[i]
            if abs(tmp_char['x0'] - char['x0']) < overlap_size and \
                    abs(tmp_char['y0'] - char['y0']) < overlap_size and \
                    abs(tmp_char['x1'] - char['x1']) < overlap_size and \
                    abs(tmp_char['y1'] - char['y1']) < overlap_size and \
                    tmp_char['text'] == char['text']:
                delete_index_list.append(char_index)
                break
    deleted_chars = []
    deleted_count = 0
    for each_delete_index in delete_index_list:
        deleted_chars.append(chars[each_delete_index - deleted_count])
        del chars[each_delete_index - deleted_count]
        deleted_count += 1
    return deleted_chars


def analyze_char_size(chars, char_size_upper=30, char_size_lower=3, default_char_size=12):
    char_sizes = []
    dcs = Decimal(default_char_size)
    for char in chars:
        cs_tmp = char['width'] / char['adv']
        if not (char_size_lower <= cs_tmp <= char_size_upper):
            cs_tmp = char['size']
        if not (char_size_lower <= cs_tmp <= char_size_upper):
            cs_tmp = dcs
        char_sizes.append(cs_tmp)
    ave_cs = max(set(char_sizes), key=char_sizes.count) if char_sizes else dcs
    min_cs = min(char_sizes) if char_sizes else dcs
    return ave_cs, min_cs


def analyze_page_orientation(plumber_page):
    """
    :param plumber_page: pdfplumber.page.Page class
    :return:
    """
    page_width = plumber_page.width
    page_height = plumber_page.height
    orientation = PAGE_LANDSCAPE if page_width >= page_height else PAGE_PORTRAIT
    return orientation


def analyze_page_num_word(phrases, page_height, page_width, top_fraction=Decimal(0.7),
                          left_fraction=Decimal(0.4), right_fraction=Decimal(0.6)):
    pagination_phrases = []
    if phrases and PAGE_NUM_RE.findall(phrases[-1]['text']):
        for phrase in reversed(phrases):
            if phrase['bottom'] >= page_height * top_fraction and \
                    phrase['x0'] >= page_width * left_fraction and \
                    phrase['x1'] <= page_width * right_fraction:
                pagination_phrases.append(phrase)
            else:
                break
    return pagination_phrases


def edges_to_lines(edges):
    h_lines, v_lines = [], []
    for i in edges:
        if i['orientation'] == 'h':
            if i not in h_lines:
                h_lines.append(i)
        else:
            if i not in v_lines:
                v_lines.append(i)
    return h_lines, v_lines


def remove_single_lines(lines, max_double=3, min_double=0.05, vertical_double=2, m='h'):
    new_lines = []
    key_1 = 'y0' if m == 'h' else 'x0'
    key_2 = 'x0' if m == 'h' else 'y0'
    key_3 = 'x1' if m == 'h' else 'y1'
    for i, li in enumerate(lines):
        if li not in new_lines:
            nearest_lines = list(filter(
                lambda x:
                    min_double < abs(li[key_1] - x[key_1]) <= max_double
                    and abs(li[key_2] - x[key_2]) <= vertical_double
                    and abs(li[key_3] - x[key_3]) <= vertical_double
                    and li != x, lines[:]
            ))
            if nearest_lines:
                new_lines.append(li)
                new_lines.extend(nearest_lines)
    return new_lines


def curve_to_lines(curves):
    h_curves, v_curves = [], []
    for i in curves:
        if 'x0' not in i or 'x1' not in i or 'top' not in i or 'bottom' not in i:
            continue
        h_curves.extend([
            {'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': i['top'], 'bottom': i['top']},
            {'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': i['bottom'], 'bottom': i['bottom']}
        ])
        v_curves.extend([
            {'orientation': 'v', 'x0': i['x0'], 'x1': i['x0'], 'top': i['top'], 'bottom': i['top']},
            {'orientation': 'v', 'x0': i['x1'], 'x1': i['x1'], 'top': i['bottom'], 'bottom': i['bottom']}
        ])
        if 'points' in i:
            for kk in i['points']:
                v_curves.append({'orientation': 'v', 'x0': kk[0], 'x1': kk[0], 'top': i['top'], 'bottom': i['bottom']})
                h_curves.append({'orientation': 'h', 'x0': i['x0'], 'x1': i['x1'], 'top': kk[1], 'bottom': kk[1]})
    return h_curves, v_curves


def convert_plumber_table(pdf_page, table, pid=1, tid=1, config=None, min_cs=1, ave_cs=6):
    if table is None:
        return None
    table_rows = []
    for row in table.rows:
        table_row = []
        table_row_dict = []
        for cell in row.cells:
            if not cell:
                table_row.append(cell)
                table_row_dict.append(cell)
                continue
            c_w = cell[2] - cell[0]
            c_h = cell[3] - cell[1]
            if c_w < min_cs or c_h < min_cs:
                continue
            cell_region = pdf_page.filter(
                lambda x: 'top' in x and 'bottom' in x and 'x0' in x and 'x1' in x and
                          x['top'] >= cell[1] - (x['bottom'] - x['top']) / 2 and
                          x['bottom'] <= cell[3] + (x['bottom'] - x['top']) / 2 and
                          x['x0'] >= cell[0] - (x['x1'] - x['x0']) / 2 and
                          x['x1'] <= cell[2] + (x['x1'] - x['x0']) / 2
            )
            text = cell_region.extract_text(y_tolerance=ave_cs * 2 / 3)
            text = text.strip().replace('\n', '<br>') if text else ''
            text = '……' if text == '„„' else text
            bbox = (cell[0], cell[1], cell[2], cell[3])
            table_row_dict.append({'width': c_w, 'height': c_h, 'text': text})
            table_row.append(Cell(bbox=bbox, text=text))
        if table_row_dict and not all(v is None for v in table_row_dict):
            table_rows.append(table_row)
    return Table(table_rows, pid=pid, tid=tid, config=config)


def merge_page_figures(pdf_page, tables_raw=None, logo=None, min_width=3, min_height=3, pid=1):
    logo_figures, figures_in_table = [], []
    fig_merge = pdf_page.figures
    figures_ori = pdf_page.images
    for idx, i in enumerate(figures_ori):
        if i is None:
            continue
        if 'srcsize' in i and (i['srcsize'][0] <= min_width or i['srcsize'][1] <= min_height):
            figures_ori[idx] = None
            continue
        # merge properties of the same figure & image
        replace_trigger = False
        if 'x0' not in i:
            img_tmp = {k: v for k, v in i.items() if k in ['height', 'width']}
            for j in fig_merge:
                if img_tmp.items() <= j.items():
                    figures_ori[idx].update(j)
                    replace_trigger = True
                    break
            if not replace_trigger:
                log.debug('merge_page_figures: figure ignored in page {0}'.format(pid))
                figures_ori[idx] = None
        # check if image within table region
        if tables_raw:
            for table in tables_raw:
                if figures_ori[idx]['top'] >= table.bbox[1] and \
                        figures_ori[idx]['bottom'] <= table.bbox[3]:
                    figures_in_table.append(figures_ori[idx])
        # check if the image is a logo
        if logo:
            img_tmp = {k: v for k, v in i.items() if k in PDF_IMAGE_KEYS}
            if img_tmp in logo:
                logo_figures.append(figures_ori[idx])
    figures_raw = sorted([
        i for i in figures_ori
        if i not in figures_in_table and i not in logo_figures and i is not None
    ], key=lambda x: x['top'])
    return figures_raw


def calculate_paragraph_border(depdf_page_object):
    tables_raw = depdf_page_object.tables_raw
    images_raw = depdf_page_object.images_raw
    ave_cs = depdf_page_object.ave_cs
    pagination_phrases = depdf_page_object.pagination_phrases
    phrases = depdf_page_object.phrases
    same = depdf_page_object.same
    page_width = depdf_page_object.width
    page_height = depdf_page_object.height
    same_tmp = depdf_page_object.same_tmp
    table_words = depdf_page_object._table_phrases
    image_words = depdf_page_object._image_phrases

    tts, tbs, lls, lrs = [], [], [], []
    tt = tb = ll = lr = None  # top-top, top-bottom, left-left, left-right
    for i in phrases:
        if (same and i in same_tmp) or i in image_words or i in pagination_phrases:
            continue
        inside = 0
        for idx, table in enumerate(tables_raw):
            if table.bbox[1] <= (i['top'] + i['bottom']) / 2 <= table.bbox[3]:
                inside = 1
                table_words.append(i)
        for img in images_raw:
            if 'bbox' in img and i['top'] >= img['bbox'][1] - ave_cs and i['bottom'] <= img['bbox'][3] + ave_cs:
                image_words.append(i)
                inside = 1
        if inside:
            continue
        tts.append(i['top'])
        tbs.append(i['bottom'])
        lls.append(i['x0'])
        lrs.append(i['x1'])
        tt = i['top'] if tt is None else tt
        tb = i['bottom'] if tb is None else tb
        ll = i['x0'] if ll is None else ll
        lr = i['x1'] if lr is None else lr
        tt = i['top'] if i['top'] < tt else tt
        tb = i['bottom'] if i['bottom'] > tb else tb
        ll = i['x0'] if i['x0'] < ll else ll
        lr = i['x1'] if i['x1'] > lr else lr
    tt = 0 if tt is None else tt
    tb = page_height if tb is None else tb
    ll = 0 if ll is None else ll
    lr = page_width if lr is None else lr
    ll_mc = Counter(sorted([int(i) for i in lls])).most_common(5)
    lr_mc = Counter(sorted([int(i) for i in lrs])).most_common(1)
    lls = [k[0] for k in ll_mc if k[1] >= 5] if ll_mc else []
    ll = Decimal(min(lls)) if lls else ll
    lr = Decimal(lr_mc[0][0]) if lr_mc else lr
    lr = page_width * 4 / 5 if lr <= page_width * 7 / 10 else lr
    return ll, tt, lr, tb


def format_text(text):
    return text.strip().replace('\xa0', '')
