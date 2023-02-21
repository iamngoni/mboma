#
#  more_welcome_options_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 21/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.how_it_works_dialog import HowItWorksDialog
from services.dialogs.my_account_dialog import MyAccountDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton


class MoreWelcomeOptionsDialog(WhatsAppDialog):
    name: str = "more_welcome_options_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):
        session.dialog_name = self.name
        session.save()

        return InteractiveButtonMessage(
            text="More Options 👇🏿👇🏿👇🏿",
            phone_number=incoming_message.from_phone_number,
            buttons=[
                ReplyButton(button_id="my_account", title="Account Information"),
                ReplyButton(button_id="how_it_works", title="How It Works"),
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

            if option_selected == "my_account":
                return MyAccountDialog()

            if option_selected == "how_it_works":
                return HowItWorksDialog()

            from services.dialogs.welcome_dialog import WelcomeDialog

            return WelcomeDialog()
