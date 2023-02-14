#
#  go_to_checkout_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.
from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.confirm_order_dialog import ConfirmOrderDialog
from services.dialogs.product_categories_dialog import ProductCategoriesDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton


class GoToCheckoutDialog(WhatsAppDialog):
    name = "go_to_checkout_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        return InteractiveButtonMessage(
            phone_number=incoming_message.from_phone_number,
            text="You can checkout now or add more products to your cart",
            buttons=[
                ReplyButton(button_id="checkout", title="Checkout Now"),
                ReplyButton(button_id="add_more_products", title="Add More Products"),
            ],
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        option_selected = incoming_message.button_reply.get("id")
        if option_selected == "checkout":
            return ConfirmOrderDialog()

        if option_selected == "add_more_products":
            return ProductCategoriesDialog()
