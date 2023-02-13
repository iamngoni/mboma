#
#  my_orders_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 13/2/2023.


from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveListMessage, TextMessage
from users.models import User


class MyOrdersDialog(WhatsAppDialog):
    name = "my_orders_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        user = User.get_user_by_phone_number(incoming_message.from_phone_number)
        if user:
            orders = user.orders.all()

            if orders.count() > 0:

                orders_text = ""
                for index, order in enumerate(orders):
                    orders_text += (
                        f"*Order {index+1}*\nOrder ID: {order.id}\n\n2 x Item 1 ($70)\n3 x Item 2 ("
                        f"$50)\n\nTotal: ${120}\nPaid using *Ecocash*\n"
                    )

                return TextMessage(
                    phone_number=incoming_message.from_phone_number,
                    text=f"*🛍️ {user.get_full_name()} Orders*\n\n" f"{orders_text}",
                )
            else:
                return TextMessage(
                    phone_number=incoming_message.from_phone_number,
                    text="You haven't made any order so far.",
                )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number,
                text="No user account associated with this session",
            )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        return MyOrdersDialog()
