from django_rq import job
from rq import Retry
from loguru import logger
from decouple import config
import requests

from services.whatsapp.messages import ReactionMessage, TextMessage
from services.whatsapp.whatsapp_message import WhatsappMessage
from shop.models import Order


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


@job("default", retry=Retry(max=3))
def send_order_confirmation_text(
    order: Order,
):
    try:
        logger.info(f"Sending order confirmation to {order.user.phone_number}")
        text_message = TextMessage(
            phone_number=order.user.phone_number,
            text=f"*Thank you for your order.*\n\nYour payment of ${order.amount} has been received."
            f"\n\n{order.narration}\n\nYour order will be delivered to you shortly.",
        )

        message = WhatsappMessage(text_message.to_json())
        message.send()

    except Exception as exc:
        logger.error(exc)
        raise
