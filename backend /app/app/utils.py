import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

import emails
from emails.template import JinjaTemplate
from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)


# -------------------------------
# Send email
# -------------------------------
def send_email(
    email_to: str,
    subject_template: str,
    html_template: str,
    environment: Dict[str, Any] = {},
) -> None:
    """Send an email using SMTP configuration."""
    if not settings.EMAILS_ENABLED:
        raise RuntimeError("Email sending is disabled. Check configuration.")

    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )

    smtp_options = {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "tls": settings.SMTP_TLS,
    }

    if settings.SMTP_USER and settings.SMTP_PASSWORD:
        smtp_options.update({
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
        })

    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logger.info("Send email result: %s", response)


# -------------------------------
# Specific email templates
# -------------------------------
def send_test_email(email_to: str) -> None:
    subject = f"{settings.PROJECT_NAME} - Test email"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html"
    template_str = template_path.read_text()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, username: str, token: str) -> None:
    subject = f"{settings.PROJECT_NAME} - Password recovery for user {username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html"
    template_str = template_path.read_text()
    link = f"{settings.SERVER_HOST}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    subject = f"{settings.PROJECT_NAME} - New account for user {username}"
    template_path = Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html"
    template_str = template_path.read_text()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


# -------------------------------
# Password reset tokens
# -------------------------------
def generate_password_reset_token(email: str) -> str:
    """Generate a JWT token for password reset."""
    expires = datetime.utcnow() + timedelta(hours=set
