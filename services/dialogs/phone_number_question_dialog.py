#
#  phone_number_question_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.payment_dialog import PaymentDialog
from services.dialogs.payment_number_dialog import PaymentNumberDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton


class PhoneNumberQuestionDialog(WhatsAppDialog):
    name = "phone_number_question_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        return InteractiveButtonMessage(
            phone_number=incoming_message.from_phone_number,
            text="Which mobile number will you be using to complete the payment for your order?",
            buttons=[
                ReplyButton(button_id="current_number", title="Same As WhatsApp"),
                ReplyButton(button_id="other", title="Other"),
            ],
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        option_selected = incoming_message.button_reply.get("id")
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            incoming_message.from_phone_number
        )

        if option_selected == "current_number":
            session.payload["payment_number"] = incoming_message.from_phone_number
            session.save()
            return PaymentDialog()

        if option_selected == "other":
            session.stage == "payment"
            session.save()
            return PaymentNumberDialog()
