from django_rq import job
from rq import Retry
from loguru import logger
from decouple import config
import requests

from services.whatsapp.messages import ReactionMessage
from services.whatsapp.whatsapp_message import WhatsappMessage


@job("default", retry=Retry(max=3))
def mark_message_as_read(message_id: str, phone_number: str):
    try:
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }

        # blue tick
        WhatsappMessage(payload).send()

        # funny reaction
        WhatsappMessage(
            ReactionMessage(phone_number=phone_number, message_id=message_id).to_json()
        ).send()

    except Exception as exc:
        logger.error(f"Error marking message as read: {exc}")
