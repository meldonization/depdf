class PDFTypeError(TypeError):

    def __init__(self, value):
        super().__init__('DePDF pdf: "{}"'.format(str(value)))


class ConfigTypeError(TypeError):

    def __init__(self, value):
        super().__init__('DePDF config: "{}"'.format(value))


class PageTypeError(TypeError):

    def __init__(self, value):
        super().__init__('DePDF page: "{}"'.format(str(value)))


class BoxValueError(ValueError):

    def __init__(self, value):
        super().__init__('DePDF bbox: "{}"'.format(value))
