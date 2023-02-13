#
#  email_address_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.welcome_dialog import WelcomeDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage


class EmailAddressDialog(WhatsAppDialog):
    name = "email_address_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):
        session.dialog_name = self.name
        session.save()

        return TextMessage(
            text="For communication and information updates enter your email address.\n\nPlease note that your email "
            "address will not be shared with any third party...",
            phone_number=incoming_message.from_phone_number,
        )

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
    ):
        return WelcomeDialog()
