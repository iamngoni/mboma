#
#  payment_method_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.phone_number_question_dialog import PhoneNumberQuestionDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveButtonMessage
from services.whatsapp.reply_button import ReplyButton


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
        logger.info(f"payment method -> {option_selected}")

        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            incoming_message.from_phone_number
        )
        session.payload["payment_method"] = option_selected
        session.save()

        logger.info(session)

        return PhoneNumberQuestionDialog()
