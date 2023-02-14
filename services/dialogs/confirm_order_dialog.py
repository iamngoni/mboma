#
#  confirm_order_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.payment_method_dialog import PaymentMethodDialog
from services.dialogs.welcome_dialog import WelcomeDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage, InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton
from users.models import User


class ConfirmOrderDialog(WhatsAppDialog):
    name = "confirm_order_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        user = User.get_user_by_phone_number(incoming_message.from_phone_number)
        if user:

            cart_text = ""
            for cart_item in user.cart.items.all():
                cart_text += f"{cart_item.quantity} x {cart_item.product.name} ${cart_item.total}\n"

            logger.info(cart_text)

            return InteractiveButtonMessage(
                phone_number=incoming_message.from_phone_number,
                text=f"*🛍️ Cart*\n\n{cart_text}\nTotal: ${user.cart.total}",
                buttons=[
                    ReplyButton(button_id="confirm", title="Confirm"),
                    ReplyButton(button_id="cancel ", title="Cancel"),
                    ReplyButton(
                        button_id="cancel_and_clear_cart", title="Cancel & Clear Cart"
                    ),
                ],
            )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text="No user associated with this session found.",
            )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        option_selected = incoming_message.button_reply.get("id")
        logger.info(option_selected)

        if option_selected == "confirm":
            return PaymentMethodDialog()

        if option_selected == "cancel":
            return WelcomeDialog()
        if option_selected == "cancel_and_clear_cart":
            user = User.get_user_by_phone_number(incoming_message.from_phone_number)
            if user:
                user.cart.delete()
            return WelcomeDialog()
