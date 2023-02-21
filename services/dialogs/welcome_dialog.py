#
#  welcome_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.more_welcome_options_dialog import MoreWelcomeOptionsDialog
from services.dialogs.my_orders_dialog import MyOrdersDialog
from services.dialogs.product_categories_dialog import ProductCategoriesDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton


class WelcomeDialog(WhatsAppDialog):
    name: str = "welcome_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):
        session.dialog_name = self.name
        session.save()

        return InteractiveButtonMessage(
            text="Welcome to Tregers!!\n\nYou may browse our products catalog and purchase right here 📍 right now 🥳 "
            "on WhatsApp.\n\nTo continue use the options below 👇🏿👇🏿👇🏿",
            phone_number=incoming_message.from_phone_number,
            buttons=[
                ReplyButton(
                    button_id="start_shopping_on_whatsapp", title="Shop on WhatsApp"
                ),
                ReplyButton(button_id="my_orders", title="My Orders"),
                ReplyButton(button_id="more", title="More Options"),
            ],
        )

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
    ):
        if not previous_dialog_name:
            return self
        else:
            option_selected = incoming_message.button_reply.get("id")
            if option_selected == "start_shopping_on_whatsapp":
                # commented out because whatsapp couldn't allow me to continue with this method
                # return ProductsDialog()
                return ProductCategoriesDialog()

            if option_selected == "my_orders":
                return MyOrdersDialog()

            if option_selected == "more":
                return MoreWelcomeOptionsDialog()
