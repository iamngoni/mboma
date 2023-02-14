#
#  payment_number_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.payment_dialog import PaymentDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage


class PaymentNumberDialog(WhatsAppDialog):
    name = "payment_number_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        return TextMessage(
            phone_number=incoming_message.from_phone_number,
            text="Enter mobile number to complete payment",
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        phone_number = incoming_message.message
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            incoming_message.from_phone_number
        )
        session.payload["payment_number"] = phone_number
        session.save()

        return PaymentDialog()
