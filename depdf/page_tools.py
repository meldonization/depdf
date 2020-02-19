from decimal import Decimal

PAGE_PORTRAIT = 'portrait'
PAGE_LANDSCAPE = 'landscape'


def remove_duplicate_chars(chars, overlap_size=3):
    # 去除通过叠加字符来实现加粗的多余字符
    delete_index_list = []
    deleted_count = 0
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
    for each_delete_index in delete_index_list:
        del chars[each_delete_index - deleted_count]
        deleted_count += 1


def analysis_char_size(chars, char_size_upper=30, char_size_lower=3, default_char_size=12):
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


def analysis_page_orientation(plumber_page):
    """
    :param plumber_page: pdfplumber.page.Page class
    :return:
    """
    page_width = plumber_page.width
    page_height = plumber_page.height
    orientation = PAGE_LANDSCAPE if page_width >= page_height else PAGE_PORTRAIT
    return orientation
