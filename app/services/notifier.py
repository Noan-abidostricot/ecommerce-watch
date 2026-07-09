import logging
from email.message import EmailMessage

import aiosmtplib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.alert import Alert

logger = logging.getLogger(__name__)


async def get_unsent_alerts(session: AsyncSession) -> list[Alert]:
    result = await session.execute(select(Alert).where(Alert.sent.is_(False)))
    return list(result.scalars().all())


def compose_message(alerts: list[Alert]) -> str:
    lines = [f"{len(alerts)} alerte(s) détectée(s) :", ""]
    for alert in alerts:
        lines.append(f"- [{alert.alert_type}] {alert.message}")
    return "\n".join(lines)


async def send_email(subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = settings.alert_recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user,
        password=settings.smtp_password,
        start_tls=True,
    )


async def send_notifications(session: AsyncSession) -> None:
    alerts = await get_unsent_alerts(session)
    if not alerts:
        return

    body = compose_message(alerts)
    try:
        await send_email(f"[E-commerce Watch] {len(alerts)} alerte(s)", body)
    except Exception:
        logger.exception("Échec d'envoi de l'email — nouvel essai au prochain cycle")
        return

    for alert in alerts:
        alert.sent = True
    logger.info("%d alerte(s) envoyée(s)", len(alerts))
