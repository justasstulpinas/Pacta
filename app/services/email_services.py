import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM = os.getenv("EMAIL_FROM", "noreply@melno.app")
APP_URL = os.getenv("APP_URL", "https://melno.app")

_S = "font-family:'Syne',Arial,sans-serif;"


def _digit_row(code: str) -> str:
    """Six #1E1E1E boxes (24×30 px, 5 px radius, 7 px gap) — centered."""
    boxes = "".join(
        f'<td style="padding:0 3.5px;">'
        f'<div style="width:24px;height:30px;line-height:30px;background:#1E1E1E;'
        f'border-radius:5px;font-size:14px;font-weight:700;color:#F4F4F4;'
        f'font-family:monospace;text-align:center;">{d}</div></td>'
        for d in code
    )
    return (
        f'<table cellpadding="0" cellspacing="0" style="margin:0 auto;">'
        f'<tr>{boxes}</tr></table>'
    )


def _pill_button(url: str, label: str) -> str:
    """#D9D9D9 pill button centered — matches Figma spec."""
    return (
        f'<table cellpadding="0" cellspacing="0" style="margin:0 auto;">'
        f'<tr><td bgcolor="#D9D9D9" style="border-radius:100px;">'
        f'<a href="{url}" style="display:inline-block;padding:6px 30px;'
        f'{_S}font-size:12px;font-weight:400;color:#1E1E1E;'
        f'text-decoration:none;letter-spacing:-0.02em;white-space:nowrap;'
        f'border-radius:100px;">{label}</a>'
        f'</td></tr></table>'
    )


def _base(content: str) -> str:
    """
    Outer #1E1E1E wrapper → logo (img + melno text) → #2A2A2A card (15 px radius).
    Max card width 408 px, centred. Matches Figma mail spec.
    """
    return f"""<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700&display=swap');
  body{{margin:0;padding:0;background:#1E1E1E;-webkit-text-size-adjust:100%;}}
</style>
</head>
<body style="margin:0;padding:0;background:#1E1E1E;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#1E1E1E;padding:16px 0;">
  <tr><td align="center">
    <table width="408" cellpadding="0" cellspacing="0" style="max-width:408px;width:100%;">

      <!-- Logo -->
      <tr><td style="padding:9px 0 16px 0;">
        <table cellpadding="0" cellspacing="0"><tr>
          <td style="padding-right:10px;vertical-align:middle;">
            <img src="{APP_URL}/logo-icon.png" width="40" height="40" alt="Melno"
                 style="border-radius:50%;display:block;border:0;" />
          </td>
          <td style="vertical-align:middle;">
            <span style="{_S}font-size:19px;font-weight:400;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
              melno
            </span>
          </td>
        </tr></table>
      </td></tr>

      <!-- Card -->
      <tr><td style="background:#2A2A2A;border-radius:15px;padding:28px 24px;">
        {content}
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>"""


# ── Auth & system emails (keep working, updated to new base) ──────────────────

def send_submission_notification(owner_email: str, template_name: str, submission_id: int):
    content = f"""
      <h1 style="margin:0 0 12px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Nauja sutartis pateikta
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:18px;">
        Klientas užpildė ir pateikė sutartį pagal šabloną
        <strong style="color:#F4F4F4;">{template_name}</strong>.
      </p>
      <div style="height:8px;"></div>
      {_pill_button(f"{APP_URL}/dashboard/submissions/{submission_id}", "Peržiūrėti sutartį")}
    """
    resend.Emails.send({
        "from": FROM,
        "to": [owner_email],
        "subject": f"Nauja sutartis pateikta — {template_name}",
        "html": _base(content),
    })


def send_submission_confirmation(submitter_email: str, template_name: str):
    content = f"""
      <h1 style="margin:0 0 12px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Sutartis patvirtinta
      </h1>
      <p style="margin:0;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:18px;">
        Jūsų pateikta sutartis pagal šabloną
        <strong style="color:#F4F4F4;">{template_name}</strong>
        buvo peržiūrėta ir patvirtinta kitos šalies.
      </p>
    """
    resend.Emails.send({
        "from": FROM,
        "to": [submitter_email],
        "subject": f"Sutartis patvirtinta — {template_name}",
        "html": _base(content),
    })


def send_verification_reminder(email: str, token: str):
    verification_url = f"{APP_URL}/verify-email?token={token}"
    content = f"""
      <h1 style="margin:0 0 12px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Liko 24 valandos patvirtinti el. paštą
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:18px;">
        Jūsų paskyra bus sustabdyta po 24 valandų, jei nepatvirtinsite el. pašto adreso.
      </p>
      {_pill_button(verification_url, "Patvirtinti el. paštą")}
    """
    resend.Emails.send({
        "from": FROM,
        "to": [email],
        "subject": "⚠️ Patvirtinkite el. paštą — liko 24h",
        "html": _base(content),
    })


def send_email_verification(email: str, token: str):
    verification_url = f"{APP_URL}/verify-email?token={token}"
    content = f"""
      <h1 style="margin:0 0 12px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Patvirtinkite el. paštą
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:18px;">
        Paspauskite mygtuką, kad aktyvuotumėte Melno paskyrą. Nuoroda galioja 24 valandas.
      </p>
      {_pill_button(verification_url, "Patvirtinti el. paštą")}
    """
    resend.Emails.send({
        "from": FROM,
        "to": [email],
        "subject": "Patvirtinkite el. paštą — Melno",
        "html": _base(content),
    })


def send_password_reset(email: str, token: str):
    reset_url = f"{APP_URL}/reset-password?token={token}"
    content = f"""
      <h1 style="margin:0 0 12px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Slaptažodžio atstatymas
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:18px;">
        Gavome prašymą atstatyti slaptažodį. Nuoroda galioja 1 valandą.
      </p>
      {_pill_button(reset_url, "Atstatyti slaptažodį")}
    """
    resend.Emails.send({
        "from": FROM,
        "to": [email],
        "subject": "Slaptažodžio atstatymas — Melno",
        "html": _base(content),
    })


# ── Signing flow emails ───────────────────────────────────────────────────────

def send_signing_invitation(
    recipient_email: str,
    template_name: str,
    signing_url: str,
    access_code: str,
    expires_at,
    owner_name: str | None = None,
):
    sender_line = (
        f"{owner_name} atsiuntė jums sutartį. pasirašykite ir gausite sutartį iškart."
        if owner_name
        else "Jums išsiųsta sutartis pasirašymui."
    )
    content = f"""
      <h1 style="margin:0 0 8px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Užtruksite vos kelias minutes
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:14px;">
        {sender_line}
      </p>

      <p style="margin:0 0 8px;{_S}font-size:12px;color:#FFFFFF;letter-spacing:-0.02em;line-height:14px;">
        Patvirtinimo kodas
      </p>
      {_digit_row(access_code)}

      <div style="height:16px;"></div>
      {_pill_button(signing_url, "Atidaryti sutartį")}
      <div style="height:16px;"></div>

      <p style="margin:0;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:14px;">
        Kodas galioja iki nuorodos galiojimo pabaigos. Neatskleisite šio kodo niekam.
      </p>
    """
    resend.Emails.send({
        "from": FROM,
        "to": [recipient_email],
        "subject": f"Sutartis pasirašymui — {template_name}",
        "html": _base(content),
    })


def send_owner_signed_notification(
    owner_email: str,
    template_name: str,
    download_url: str,
    download_code: str,
):
    content = f"""
      <h1 style="margin:0 0 8px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Formalumai užbaigti!
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:14px;">
        Jūsų sutartis buvo pasirašyta. Ją lengvai galite atsisiųsti suvedus kodą.
      </p>

      <p style="margin:0 0 8px;{_S}font-size:12px;color:#FFFFFF;letter-spacing:-0.02em;line-height:14px;">
        Patvirtinimo kodas
      </p>
      {_digit_row(download_code)}

      <div style="height:16px;"></div>
      {_pill_button(download_url, "Atidaryti sutartį")}
      <div style="height:16px;"></div>

      <table width="100%" cellpadding="0" cellspacing="0">
        <tr><td style="background:#4D3636;border-radius:15px;padding:14px 18px;">
          <p style="margin:0;{_S}font-size:12px;color:#D7A1A1;letter-spacing:-0.02em;line-height:14px;">
            Sutartį galima atsisiųsti tik kartą, įsitikinkite kad ją išsaugote tinkamoje vietoje,
            atsisiuntimo kodas galioja tik vieną kartą.
          </p>
        </td></tr>
      </table>
    """
    resend.Emails.send({
        "from": FROM,
        "to": [owner_email],
        "subject": f"Sutartis pasirašyta — {template_name}",
        "html": _base(content),
    })


def send_contract_declined(owner_email: str, template_name: str, template_id: int | None = None):
    link_url = (
        f"{APP_URL}/dashboard/templates/{template_id}/link"
        if template_id
        else f"{APP_URL}/dashboard/templates"
    )
    content = f"""
      <h1 style="margin:0 0 8px;{_S}font-size:19px;font-weight:700;color:#F4F4F4;letter-spacing:-0.03em;line-height:23px;">
        Kažkas užkliuvo...
      </h1>
      <p style="margin:0 0 20px;{_S}font-size:12px;color:#BCBCBC;letter-spacing:-0.02em;line-height:14px;">
        Klientas peržiūrėjo ir atmetė jūsų sutartį. Sutartis nebuvo pasirašyta.
        Galite susisiekti su klientu ir išsiaiškinti priežastis, arba sukurti naują nuorodą.
      </p>
      {_pill_button(link_url, "Generuoti naują")}
    """
    resend.Emails.send({
        "from": FROM,
        "to": [owner_email],
        "subject": f"Sutartis atmesta — {template_name}",
        "html": _base(content),
    })
