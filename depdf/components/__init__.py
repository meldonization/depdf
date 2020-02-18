from depdf.components.paragraph import Paragraph
from depdf.components.text import Text
from depdf.components.span import Span
from depdf.components.table import Table, Cell

component_list = [
    Paragraph,
    Table,
    Span,
    Text,
    Cell,
]

__all__ = [
    'Paragraph', 'Table', 'Span', 'Text', 'Cell',
]
