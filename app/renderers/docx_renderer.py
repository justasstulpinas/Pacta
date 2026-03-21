from docx import Document
from bs4 import BeautifulSoup
from io import BytesIO

def render_docx_from_html(html:str) ->bytes:
    soup = BeautifulSoup(html, 'html.parser')

    document = Document()

    body = soup.find('body')

    if not body:
        return b''
    
    for element in body.descendants:
        if element.name == 'h1':
            document.add_heading(element.get_text(), level=1)
        elif element.name == 'h2':
            document.add_heading(element.get_text(), level=2)
        elif element.name == 'h3':
            document.add_heading(element.get_text(), level=3)
        elif element.name == 'p':
            document.add_paragraph(element.get_text())
        elif element.name == 'br':
            document.add_paragraph()

    buffer = BytesIO()

    document.save(buffer)

    return buffer.getvalue()