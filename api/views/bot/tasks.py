from paynow import Paynow
import time

from decouple import config
from django_rq import job
from loguru import logger
from rq import Retry

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


@job("paynow", retry=Retry(max=3))
def continuously_poll_paynow_transaction(order: Order, poll_url: str):
    try:
        transaction_paid_up = False
        transaction_check_count = 0

        paynow = Paynow(
            config("PAYNOW_ID"),
            config("PAYNOW_KEY"),
            "https://modestnerd.co",
            "https://mboma.modestnerd.co/api/1.0/paynow",
        )

        while transaction_paid_up is False and transaction_check_count < 60:
            time.sleep(10)
            transaction_check_count += 1
            logger.info(f"Polling paynow transaction: {transaction_check_count}")
            status = paynow.check_transaction_status(poll_url)
            if status.paid:
                transaction_paid_up = True
                logger.info(f"Transaction paid up: {status.paid}")

                order.status = status.status
                order.paynow_reference = status.paynow_reference
                order.poll_url = poll_url
                order.status = status.status
                order.hash = status.hash
                order.save()

                logger.info("Order updated. Sending confirmation text.")
                send_order_confirmation_text.delay(order)
            else:
                logger.info(
                    "Transaction not paid up yet. Checking again in 10 seconds."
                )

    except Exception as exc:
        logger.error(exc)
        raise
