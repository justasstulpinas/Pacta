from docx import Document
from bs4 import BeautifulSoup
from io import BytesIO

# is sugeneruoti html isrenderinamas docx failas 
def render_docx_from_html(html: str) -> bytes:
    soup = BeautifulSoup(html, "html.parser")

    document = Document()

    body = soup.find('body')

    if not body:
        return b''

    wrote_content = False

    
    contract_body = body.find(class_="contract-body")
    if contract_body:
        content_text = contract_body.get_text(separator="\n", strip=False)
        normalized_content = (
            content_text.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
        )
        if normalized_content:
            for line in normalized_content.split("\n"):
                document.add_paragraph(line)
                wrote_content = True

    footer = body.find(class_="footer")
    if footer:
        footer_text = footer.get_text(separator=' ', strip=True)
        if footer_text:
            for section in document.sections:
                if section.footer.paragraphs:
                    footer_paragraph = section.footer.paragraphs[0]
                else:
                    footer_paragraph = section.footer.add_paragraph()
                footer_paragraph.text = footer_text

  
    if not wrote_content:
        for element in body.descendants:
            if element.name == 'h1':
                document.add_heading(element.get_text(), level=1)
                wrote_content = True
            elif element.name == 'h2':
                document.add_heading(element.get_text(), level=2)
                wrote_content = True
            elif element.name == 'h3':
                document.add_heading(element.get_text(), level=3)
                wrote_content = True
            elif element.name == 'p':
                text = element.get_text(strip=True)
                if text:
                    document.add_paragraph(text)
                    wrote_content = True
            elif element.name == 'br':
                document.add_paragraph()
                wrote_content = True

    buffer = BytesIO()

    document.save(buffer)

    return buffer.getvalue()
