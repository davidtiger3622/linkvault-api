import resend

from app.core.config import settings

resend.api_key = settings.resend_api_key


def send_password_reset_email(to_email: str, reset_token: str) -> None:
    reset_link = f"{settings.frontend_url}/reset-password?token={reset_token}"
    resend.Emails.send({
        "from": "LinkVault <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Reset your LinkVault password",
        "html": f"<p>Click the link below to reset your password. This link expires in 15 minutes.</p><p><a href=\"{reset_link}\">{reset_link}</a></p>",
    })
