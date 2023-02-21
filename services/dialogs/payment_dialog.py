#
#  payment_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from decouple import config
from loguru import logger
from paynow import Paynow

from bot.models import WhatsappSession
from services.dialogs.welcome_dialog import WelcomeDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage
from shop.models import Order
from users.models import User


class PaymentDialog(WhatsAppDialog):
    name = "payment_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        user = User.get_user_by_phone_number(incoming_message.from_phone_number)

        narration = ""
        for cart_item in user.cart.items.all():
            narration += (
                f"{cart_item.quantity} x {cart_item.product.name} ${cart_item.total}\n"
            )

        logger.info(narration)
        logger.info(session)

        # create order
        order = Order(
            user=user,
            amount=user.cart.total,
            narration=narration,
        )
        order.save()

        paynow = Paynow(
            config("PAYNOW_ID"),
            config("PAYNOW_KEY"),
            "https://google.com",
            "https://mboma.modestnerd.co/api/1.0/paynow",
        )
        payment = paynow.create_payment(order.id, user.email)
        for cart_item in user.cart.items.all():
            payment.add(cart_item.product.name, cart_item.total)

        response = paynow.send(
            payment=payment,
        )
        logger.info(response)
        if response.success:
            user.cart.delete()

            link = response.redirect_url
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text=f"Please use the following link to complete your payment:\n\n{link}",
            )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text="Failed to process your order. You may try again",
            )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        return WelcomeDialog()
