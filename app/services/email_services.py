import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

def send_submission_notification(
        owner_email: str,
        template_name: str,
        submission_id: int,
):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [owner_email],
        "subject": "Your contract was submitted!",
        "html": f"<p>You have a new submission for template {template_name}. Submission ID: {submission_id}</p>",
    })
    
def send_submission_confirmation(
        submitter_email: str,
        template_name: str,
):
    resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": [submitter_email],
        "subject": "Your submission was confirmed!",
        "html": f"<p>Your submission for template {template_name}, was confirmed!</p>",
    })