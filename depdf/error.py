class PDFTypeError(TypeError):

    def __init__(self, pdf):
        super().__init__('DePDF wrong pdf "{}"'.format(str(pdf)))


class ConfigTypeError(TypeError):

    def __init__(self, config):
        super().__init__('DePDF: wrong configure "{}"'.format(config))
