from weasyprint import HTML

# is html isrenderinamas pdf failas
def render_pdf_from_html(html: str) -> bytes:

    pdf_bytes = HTML(string=html).write_pdf()

    return pdf_bytes