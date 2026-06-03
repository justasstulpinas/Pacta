import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM = os.getenv("EMAIL_FROM", "noreply@melno.lt")
APP_URL = os.getenv("APP_URL", "https://melno.lt")


def _base(content: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Melno</title>
</head>
<body style="margin:0;padding:0;background:#09090b;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#09090b;padding:40px 16px;">
    <tr><td align="center">
      <table width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;">

        <!-- Logo -->
        <tr><td style="padding-bottom:32px;">
          <span style="font-size:18px;font-weight:700;color:#ffffff;letter-spacing:-0.3px;">Melno</span>
        </td></tr>

        <!-- Card -->
        <tr><td style="background:#18181b;border:1px solid #27272a;border-radius:12px;padding:36px;">
          {content}
        </td></tr>

        <!-- Footer -->
        <tr><td style="padding-top:24px;text-align:center;">
          <p style="margin:0;font-size:11px;color:#52525b;">
            © 2026 Melno · <a href="{APP_URL}" style="color:#52525b;text-decoration:underline;">melno.lt</a>
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_submission_notification(
    owner_email: str,
    template_name: str,
    submission_id: int,
):
    content = f"""
      <h1 style="margin:0 0 8px;font-size:20px;font-weight:700;color:#ffffff;">
        Nauja sutartis pateikta
      </h1>
      <p style="margin:0 0 24px;font-size:14px;color:#a1a1aa;line-height:1.6;">
        Klientas užpildė ir pateikė sutartį pagal šabloną
        <strong style="color:#ffffff;">{template_name}</strong>.
        Peržiūrėkite pateiktus duomenis ir patvirtinkite sutartį.
      </p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr><td style="background:#09090b;border:1px solid #27272a;border-radius:8px;padding:16px;">
          <p style="margin:0 0 4px;font-size:11px;color:#71717a;text-transform:uppercase;letter-spacing:0.08em;">Sutarties ID</p>
          <p style="margin:0;font-size:15px;color:#ffffff;font-weight:600;">#{submission_id}</p>
        </td></tr>
      </table>

      <a href="{APP_URL}/dashboard/contracts"
         style="display:inline-block;background:#ffffff;color:#09090b;font-size:14px;font-weight:600;
                text-decoration:none;padding:12px 24px;border-radius:8px;">
        Peržiūrėti sutartį →
      </a>

      <p style="margin:28px 0 0;font-size:12px;color:#52525b;line-height:1.6;">
        Šis laiškas išsiųstas automatiškai, nes esate šablono savininkas.
      </p>
    """
    resend.Emails.send({
        "from": FROM,
        "to": [owner_email],
        "subject": f"Nauja sutartis pateikta — {template_name}",
        "html": _base(content),
    })


def send_submission_confirmation(
    submitter_email: str,
    template_name: str,
):
    content = f"""
      <h1 style="margin:0 0 8px;font-size:20px;font-weight:700;color:#ffffff;">
        Sutartis patvirtinta
      </h1>
      <p style="margin:0 0 24px;font-size:14px;color:#a1a1aa;line-height:1.6;">
        Jūsų pateikta sutartis pagal šabloną
        <strong style="color:#ffffff;">{template_name}</strong>
        buvo peržiūrėta ir patvirtinta kitos šalies.
      </p>

      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:28px;">
        <tr><td style="background:#052e16;border:1px solid #14532d;border-radius:8px;padding:16px;">
          <p style="margin:0;font-size:14px;color:#4ade80;line-height:1.6;">
            ✓ &nbsp;Sutartis įsigalioja nuo patvirtinimo momento.
          </p>
        </td></tr>
      </table>

      <p style="margin:0 0 0;font-size:12px;color:#52525b;line-height:1.6;">
        Išsaugokite šį laišką kaip patvirtinimą. Jei turite klausimų, susisiekite su sutarties išdavėju.
      </p>
    """
    resend.Emails.send({
        "from": FROM,
        "to": [submitter_email],
        "subject": f"Sutartis patvirtinta — {template_name}",
        "html": _base(content),
    })
