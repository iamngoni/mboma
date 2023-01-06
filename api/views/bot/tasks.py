from django_rq import job
from rq import Retry
from loguru import logger
from decouple import config
import requests


@job("default", retry=Retry(max=3))
def mark_message_as_read(message_id: str):
    try:
        headers = {
            "Authorization": f'Bearer {config("WHATSAPP_TOKEN")}',
            "Content-Type": "application/json",
        }

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id,
        }
        logger.info(f"send payload back to whatsapp -> {payload}")

        response = requests.request(
            "POST",
            f"{config('WHATSAPP_URL')}/{config('WHATSAPP_ID')}/messages",
            headers=headers,
            data=payload,
        )
        logger.info(f"response from whatsapp -> {response.text}")
    except Exception as exc:
        logger.error(f"Error marking message as read: {exc}")
