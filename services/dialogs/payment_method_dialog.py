#
#  payment_method_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from decouple import config
from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.instructions_dialog import InstructionsDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton
from paynow import Paynow

from shop.models import Order
from users.models import User


class PaymentMethodDialog(WhatsAppDialog):
    name = "payment_method_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        return InteractiveButtonMessage(
            phone_number=incoming_message.from_phone_number,
            text="Select the payment method you wish to pay for your order with between Ecocash and Onemoney",
            buttons=[
                ReplyButton(button_id="ecocash", title="Ecocash"),
                ReplyButton(button_id="onemoney", title="OneMoney"),
            ],
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        option_selected = incoming_message.button_reply.get("id")

        user = User.get_user_by_phone_number(incoming_message.from_phone_number)

        narration = ""
        for cart_item in user.cart.items.all():
            narration += (
                f"{cart_item.quantity} x {cart_item.product.name} ${cart_item.total}\n"
            )

        # create order
        order = Order(
            user=user,
            amount=user.cart.total,
            payment_method=option_selected,
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

        response = paynow.send_mobile(
            payment=payment,
            phone=incoming_message.from_phone_number,
            method=option_selected,
        )
        if response.success:
            logger.info(response.instructions)
            return InstructionsDialog()
