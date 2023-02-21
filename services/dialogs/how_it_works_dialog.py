#
#  how_it_works_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.
from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage


class HowItWorksDialog(WhatsAppDialog):
    name: str = "how_it_works_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):
        session.dialog_name = self.name
        session.save()

        return TextMessage(
            phone_number=incoming_message.from_phone_number,
            text=(
                "*Tregers ChatBot 🛒*\n\nTregers chatbot is an online service portal offered via WhatsApp to allow for "
                "Tregers customers to purchase products from the comfort of their homes and have the items delivered "
                "to them safely.\n\n︖ How do I buy on the chatbot\nYou can browse through our products catalog, "
                "add products you like to a shopping cart right here on WhatsApp and place your order. You won't be "
                "asked to leave WhatsApp except to process payment for your order on Paynow.\n\n︖ How do I pay\nAll "
                "payments for any orders placed through WhatsApp can be paid for using Ecocash or OneMoney on "
                "Paynow.\n\n︖ How can I contact you\nYou can contact us on +263783396917"
            ),
        )

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
    ):
        from services.dialogs.welcome_dialog import WelcomeDialog

        return WelcomeDialog()
