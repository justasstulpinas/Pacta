
# failaas skirtas parodyti kaip surinkta informacija per  contract submission service bus isdeliota i html 
def render_contract_html(
    *,
    content: str,
    signature_image: str | None =None,
) -> str:
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
}}

.signature-block img {{
    max-width: 300px;
    height: auto;
    border-bottom: 1px solid #ccc;
}}

.footer {{
    margin-top: 24px;
    font-size: 12px;
    color: #777;
    text-align: center;
}}

@page {{
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
<div class="contract-container">
<div class="contract-body">
{content}
</div>
{f'<div class="signature-block"><img src="data:image/png;base64,{signature_image}" alt="Signature" /></div>' if signature_image else ''}


<div class="footer">
Sugeneruota su Melno
</div>
</div>
</body>
</html>
"""
    return html