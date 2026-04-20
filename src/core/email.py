import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.core.config import settings


async def send_verification_email(to_email: str, username: str, token: str) -> None:
    verify_url = f"{settings.app_url}/api/v1/auth/verify-email?token={token}"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;background:#0a0a0f;color:#e0e0e0;padding:32px;border-radius:8px">
      <h2 style="color:#00c8ff;margin-bottom:8px">ForzaGram</h2>
      <p>Hola <strong>{username}</strong>,</p>
      <p>Confirma tu cuenta haciendo clic en el botón:</p>
      <a href="{verify_url}" style="display:inline-block;margin:16px 0;padding:12px 24px;background:#00c8ff;color:#000;font-weight:bold;text-decoration:none;border-radius:4px">
        Verificar cuenta
      </a>
      <p style="font-size:12px;color:#888">Si no creaste esta cuenta, ignora este mensaje.</p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verifica tu cuenta en ForzaGram"
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )
