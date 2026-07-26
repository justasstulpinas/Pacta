
import re
import html as _html

_SIGNATURE_RE = re.compile(r"\{\{\s*signature\s*\}\}")
_USER_SIGNATURE_RE = re.compile(r"\{\{\s*user_signature\s*\}\}")


def _sig_block(signature_image: str, signer_name: str | None) -> str:
    name_html = f'<span class="signer-name">{signer_name}</span>' if signer_name else ""
    return (
        f'<div class="signature-block">'
        f'<div class="signature-left">'
        f'<img src="data:image/png;base64,{signature_image}" alt="Signature" />'
        f'{name_html}'
        f'</div></div>'
    )


def render_contract_html(
    *,
    content: str,
    signature_image: str | None = None,
    signer_name: str | None = None,
    user_signature_image: str | None = None,
    logo_image: str | None = None,
    logo_x: float = 5.0,
    logo_y: float = 5.0,
    logo_w: float = 15.0,
    client_sig_x: float | None = None,
    client_sig_y: float | None = None,
    user_sig_x: float | None = None,
    user_sig_y: float | None = None,
) -> str:
    content = _html.unescape(content)

    # User signature — fixed position if coordinates set, else inline
    fixed_user_sig = ""
    if user_sig_x is not None and user_signature_image:
        fixed_user_sig = f'<div style="position:fixed;left:{user_sig_x}%;top:{user_sig_y}%;">{_sig_block(user_signature_image, None)}</div>'
        content = _USER_SIGNATURE_RE.sub("", content)
    elif _USER_SIGNATURE_RE.search(content):
        if user_signature_image:
            content = _USER_SIGNATURE_RE.sub(_sig_block(user_signature_image, None), content)
        else:
            content = _USER_SIGNATURE_RE.sub("", content)

    # Client signature — fixed position if coordinates set, else inline
    fixed_client_sig = ""
    inline_placed = False
    if client_sig_x is not None and signature_image:
        fixed_client_sig = f'<div style="position:fixed;left:{client_sig_x}%;top:{client_sig_y}%;">{_sig_block(signature_image, signer_name)}</div>'
        content = _SIGNATURE_RE.sub("", content)
        inline_placed = True
    elif _SIGNATURE_RE.search(content):
        if signature_image:
            content = _SIGNATURE_RE.sub(_sig_block(signature_image, signer_name), content)
            inline_placed = True
        else:
            content = _SIGNATURE_RE.sub("", content)

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Contract</title>

<style>
body {{
    font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    color: #111;
}}

@media screen {{
    html {{
        background: #c8c8c8;
    }}
    body {{
        padding: 24mm 16mm 20mm 16mm;
        min-height: 297mm;
        max-width: 210mm;
        margin: 0 auto;
        background: white;
        box-sizing: border-box;
        box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    }}
}}

.contract-container {{
    display: block;
}}

.contract-body {{
    display: block;
    margin: 0;
    word-break: break-word;
    overflow-wrap: anywhere;
    font-size: 16px;
    font-family: 'Liberation Serif', 'Times New Roman', Times, serif !important;
}}

.contract-body p,
.contract-body li,
.contract-body span,
.contract-body div {{
    font-family: 'Liberation Serif', 'Times New Roman', Times, serif;
}}

.contract-body h1 {{ font-size: 2em; font-weight: bold; margin: 0.5em 0; }}
.contract-body h2 {{ font-size: 1.5em; font-weight: bold; margin: 0.5em 0; }}
.contract-body h3 {{ font-size: 1.17em; font-weight: bold; margin: 0.5em 0; }}
.contract-body p {{ margin: 0.4em 0; }}
.contract-body ul {{ list-style: disc; padding-left: 1.5em; margin: 0.4em 0; }}
.contract-body ol {{ list-style: decimal; padding-left: 1.5em; margin: 0.4em 0; }}
.contract-body strong {{ font-weight: bold; }}
.contract-body em {{ font-style: italic; }}
.contract-body u {{ text-decoration: underline; }}
.contract-body s {{ text-decoration: line-through; }}

.signature-block {{
    margin-top: 40px;
    page-break-inside: avoid;
    display: flex;
    align-items: flex-end;
    gap: 40px;
}}

.signature-left {{
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}}

.signature-left img {{
    max-width: 240px;
    height: auto;
    border-bottom: 1px solid #ccc;
    display: block;
}}

.signature-left .signer-name {{
    font-size: 13px;
    margin-top: 4px;
    color: #333;
}}

.footer {{
    margin-top: 24px;
    font-size: 12px;
    color: #777;
    text-align: center;
}}

@page {{
    size: A4;
    margin: 24mm 16mm 20mm 16mm;
    @bottom-center {{
        content: "Sugeneruota su Melno";
        font-size: 12px;
        color: #777;
    }}
}}

@media print {{
    .footer {{
        display: none;
    }}
}}
</style>
</head>

<body>
{f'<img src="data:image/png;base64,{logo_image}" style="position:fixed;left:{logo_x}%;top:{logo_y}%;width:{logo_w}%;max-width:{logo_w}%;height:auto;object-fit:contain;z-index:100;" alt="Logo" />' if logo_image else ''}
{fixed_user_sig}
{fixed_client_sig}
<div class="contract-container">
<div class="contract-body">
{content}
</div>
{_sig_block(signature_image, signer_name) if signature_image and not inline_placed else ''}


<div class="footer">
Sugeneruota su Melno
</div>
</div>
</body>
</html>
"""
    return html