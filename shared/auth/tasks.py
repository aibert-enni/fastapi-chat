import logging
import smtplib
from email.message import EmailMessage

from fastapi import status

from shared.celery import celery
from shared.error.custom_exceptions import (
    APIError,
    ServiceUnavailableError,
    ValidationError,
)
from shared.settings import settings

logger = logging.getLogger("uvicorn")


@celery.task
def send_email(to: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = settings.email.GMAIL_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(settings.email.GMAIL_USER, settings.email.GMAIL_APP_PASSWORD)
            smtp.send_message(message)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"Error with email account authentication: {e}")
        raise ServiceUnavailableError(
            message="Email service unavailable, please try again later"
        )
    except smtplib.SMTPRecipientsRefused as e:
        code, message = list(e.recipients.values())[0]  # first failed reason
        logger.error(f"Error with email recipient: {message}")
        if 500 <= code < 600:
            raise ValidationError(message=f"Invalid recipient: {message.decode()}")
        elif 400 <= code < 500:  # temporary failure
            raise ServiceUnavailableError(
                message=f"Mail server temporarily refused recipient: {message.decode()}"
            )
        else:
            raise APIError(
                status_code=status.HTTP_502_BAD_GATEWAY,
                message=f"Unexpected mail server refusal: {message.decode()}",
                error="Bad Gateway error",
            )
