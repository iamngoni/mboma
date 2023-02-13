#
#  my_account_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import TextMessage
from users.models import User


class MyAccountDialog(WhatsAppDialog):
    name = "my_account_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):

        session.dialog_name = self.name
        session.save()

        user = User.get_user_by_phone_number(incoming_message.from_phone_number)
        if user:
            total_orders = user.orders.count()
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text=f"📑 *Account Information*\n\nName:\t{user.get_full_name()}\nEmail:\t{user.email}\nPhone Number:"
                f"\t{user.phone_number}\nTotal Orders: {total_orders}",
            )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text="No account associated with this session has been found ☹️.",
            )

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
        session: WhatsappSession,
    ):
        from services.dialogs.welcome_dialog import WelcomeDialog

        return WelcomeDialog()
