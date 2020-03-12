# DePDF

An ultimate pdf file disintegration tool. DePDF is designed to extract tables and paragraphs into structured markup language [eg. html] from embedding pdf pages. You can also use it to convert page/pdf to html.

Built on top of [`pdfplumber`](https://github.com/jsvine/pdfplumber)

# Table of Contents
[toc]


# Installation
`pip install depdf`

# Example
```python
from depdf import DePDF
from depdf import DePage

# general
with DePDF.load('test/test_general.pdf') as pdf
    pdf_html = pdf.to_html
    print(pdf_html)

# with dedicated configurations
c = Config(
    debug_flag=True,
    verbose_flag=True,
    add_line_flag=True
)
pdf = DePDF.load('test/test_general.pdf', config=c)
page_index = 23  # start from zero
page = pdf_file.pages[page_index]
page_soup = page.soup
print(page_soup.text)
```


# APIs
| **functions** | usage |
|:---:|---|
| `extract_page_paragraphs` | extract paragraphs from specific page |
| `extract_page_tables` | extract tables from specific page |
| `convert_pdf_to_html` | convert the entire pdf to html | 
| `convert_page_to_html` | convert specific page to html | 


# In-Depth

## In-page elements
* Paragraph
    + Text
    + Span
* Table
    + Cell
* Image

## Common properties
| **property & method** | explanation |
|:---:|---|
| `html` | converted html string |
| `soup` | converted beautiful soup |
| `bbox` | bounding box region | 
| `save_html` | write html tag to local file| 

## DePDf HTML structure
```html
<div class="{pdf_class}">
    %for <!--page-{pid}-->
        <div id="page-{}" class="{}">
            %for {html_elements} endfor%
        </div>
    endfor%
</div>
```

## DePage HTML element structure

### Paragraph
```html
<p>
    {paragraph-content}
    <span> {span-content} </span>
    ... 
</p>
```

### Table
```html
<table>
    <tr>
        <td> {cell_0_0} </td>
        <td> {cell_0_1} </td>
        ...
    </tr>
    <tr colspan=2>
        <td> {cell_1_0} </td>
        ...
    </tr>
    ...
</table>
```

### Image
```
<img src="temp_depdf/$prefix.png"></img>
```
# Appendix

## DePage element denotations
> Useful element properties within page

![page element](annotations.jpg)

## todo

* [ ] add support for multiple-column pdf page
* [ ] better table structure recognition
* [x] recognize embedded objects inside page elements