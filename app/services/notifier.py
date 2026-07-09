from sqlalchemy import select

from app.models.alert import Alert


async def get_unsent_alerts(session) -> list[Alert]:
    result = await session.execute(
        select(Alert).where(Alert.sent == False)  # noqa: E712
    )
    return list(result.scalars().all())

def compose_message(alerts: list[Alert]) -> str:
    lines = [f"{len(alerts)} alerte(s) détectée(s) :", ""]
    for alert in alerts:
        lines.append(f"- [{alert.alert_type}] {alert.message}")
    return "\n".join(lines)

async def send_notifications(session) -> None:
    alerts = await get_unsent_alerts(session)

    if not alerts:
        return

    message = compose_message(alerts)

    # Option B : on affiche au lieu d'envoyer
    print("=" * 40)
    print("EMAIL QUI SERAIT ENVOYÉ :")
    print(message)
    print("=" * 40)

    for alert in alerts:
        alert.sent = True
