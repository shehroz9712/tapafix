from __future__ import annotations

import asyncio
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings
from app.core.logger import logger

SENDGRID_SEND_URL = "https://api.sendgrid.com/v3/mail/send"


def _reset_email_body(*, token: str) -> tuple[str, str]:
    base = (settings.FRONTEND_PASSWORD_RESET_URL or "").strip().rstrip("/")
    if base:
        link = f"{base}?token={token}"
        plain = (
            "You requested a password reset.\n\n"
            f"Open this link to set a new password:\n{link}\n\n"
            "If you did not request this, you can ignore this email.\n"
        )
        html = (
            "<p>You requested a password reset.</p>"
            f'<p><a href="{link}">Reset your password</a></p>'
            "<p>If you did not request this, you can ignore this email.</p>"
        )
    else:
        plain = (
            "You requested a password reset.\n\n"
            f"Use this token in your app's reset form:\n{token}\n\n"
            "Set FRONTEND_PASSWORD_RESET_URL in .env to include a clickable link.\n"
        )
        html = f"<p>Use this token to reset your password:</p><pre>{token}</pre>"
    return plain, html


def _verification_otp_email_body(*, otp_code: str) -> tuple[str, str]:
    plain = (
        "Use this OTP to verify your email.\n\n"
        f"OTP: {otp_code}\n\n"
        f"This OTP expires in {settings.EMAIL_OTP_EXPIRE_MINUTES} minutes.\n"
    )
    html = (
        "<p>Use this OTP to verify your email.</p>"
        f"<p><strong>{otp_code}</strong></p>"
        f"<p>This OTP expires in {settings.EMAIL_OTP_EXPIRE_MINUTES} minutes.</p>"
    )
    return plain, html


async def _send_sendgrid(*, to_email: str, subject: str, plain: str, html: str) -> None:
    from_email = settings.EMAILS_FROM_EMAIL
    if not from_email:
        raise ValueError("EMAILS_FROM_EMAIL is required when using SendGrid")
    if not settings.SENDGRID_API_KEY:
        raise ValueError("SENDGRID_API_KEY is required when using SendGrid")

    payload: dict = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": from_email, "name": settings.EMAILS_FROM_NAME},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": plain},
            {"type": "text/html", "value": html},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(SENDGRID_SEND_URL, json=payload, headers=headers)
        if response.status_code >= 400:
            detail = response.text[:500] if response.text else response.reason_phrase
            raise RuntimeError(f"SendGrid error {response.status_code}: {detail}")


def _send_via_smtp(
    *,
    host: str,
    port: int,
    username: str | None,
    password: str | None,
    from_email: str,
    to_email: str,
    subject: str,
    plain: str,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(plain)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)


async def _send_smtp(*, to_email: str, subject: str, plain: str) -> None:
    from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
    if not settings.SMTP_SERVER or not from_email:
        raise ValueError("SMTP_SERVER and sender email are required for SMTP")

    await asyncio.to_thread(
        _send_via_smtp,
        host=settings.SMTP_SERVER,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        plain=plain,
    )


async def _send_mailtrap(*, to_email: str, subject: str, plain: str) -> None:
    from_email = settings.EMAILS_FROM_EMAIL or settings.MAILTRAP_USER
    if not settings.MAILTRAP_USER or not settings.MAILTRAP_PASSWORD or not from_email:
        raise ValueError(
            "MAILTRAP_USER, MAILTRAP_PASSWORD, and sender email are required for Mailtrap"
        )

    await asyncio.to_thread(
        _send_via_smtp,
        host=settings.MAILTRAP_HOST,
        port=settings.MAILTRAP_PORT,
        username=settings.MAILTRAP_USER,
        password=settings.MAILTRAP_PASSWORD,
        from_email=from_email,
        to_email=to_email,
        subject=subject,
        plain=plain,
    )


async def send_password_reset_email(*, to_email: str, token: str) -> None:
    subject = "Password reset"
    plain, html = _reset_email_body(token=token)
    provider = (settings.EMAIL_PROVIDER or "auto").strip().lower()

    try:
        if provider == "sendgrid":
            await _send_sendgrid(to_email=to_email, subject=subject, plain=plain, html=html)
            return
        if provider == "mailtrap":
            await _send_mailtrap(to_email=to_email, subject=subject, plain=plain)
            return
        if provider == "smtp":
            await _send_smtp(to_email=to_email, subject=subject, plain=plain)
            return

        if settings.SENDGRID_API_KEY:
            await _send_sendgrid(to_email=to_email, subject=subject, plain=plain, html=html)
            return
        if settings.SMTP_SERVER and settings.SMTP_USER:
            await _send_smtp(to_email=to_email, subject=subject, plain=plain)
            return
        if settings.MAILTRAP_USER and settings.MAILTRAP_PASSWORD:
            await _send_mailtrap(to_email=to_email, subject=subject, plain=plain)
            return

        logger.info(
            "Email not configured. Set EMAIL_PROVIDER and credentials; reset token for %s: %s",
            to_email,
            token,
        )
    except Exception:
        logger.exception(
            "Failed to send password reset email via provider '%s' to %s",
            provider,
            to_email,
        )


async def send_email_verification_otp(*, to_email: str, otp_code: str) -> None:
    subject = "Verify your email"
    plain, html = _verification_otp_email_body(otp_code=otp_code)
    try:
        await _send_sendgrid(to_email=to_email, subject=subject, plain=plain, html=html)
    except Exception:
        logger.exception("Failed to send verification OTP via SendGrid to %s", to_email)
