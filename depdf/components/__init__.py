from depdf.components.paragraph import Paragraph
from depdf.components.text import Text
from depdf.components.span import Span
from depdf.components.table import Table, Cell
from depdf.components.image import Image

component_list = [
    Paragraph,
    Table,
    Span,
    Text,
    Cell,
    Image,
]

__all__ = [
    'Paragraph', 'Table', 'Span', 'Text', 'Cell', 'Image',
]
