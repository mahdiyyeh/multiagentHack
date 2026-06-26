from __future__ import annotations

from backend import config


def send_enquiry(body: str) -> dict:
    if config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_TO_NUMBER:
        try:
            from twilio.rest import Client

            client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
            msg = client.messages.create(
                body=body[:1500],
                from_=config.TWILIO_FROM_NUMBER,
                to=config.TWILIO_TO_NUMBER,
            )
            return {"twilio_sent": True, "sid": msg.sid}
        except Exception as exc:
            return {"twilio_sent": False, "error": str(exc)}
    return {"twilio_sent": False}


def build_mailto(subject: str, body: str) -> str:
    import urllib.parse

    to = config.ENQUIRY_TO_EMAIL or "enquiry@example.com"
    return f"mailto:{to}?{urllib.parse.urlencode({'subject': subject, 'body': body})}"
