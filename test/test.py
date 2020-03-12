from depdf import *

with DePDF.load('test/test.pdf') as pdf:
    pdf.save_html()
