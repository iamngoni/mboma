#
#  whatsapp_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from abc import ABC
from typing import Optional

from bot.models import WhatsappSession
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.whatsapp_message import WhatsappMessage


class WhatsAppDialog(ABC):
    def dialog_message(self, incoming_message: WhatsAppMessageDTO):
        raise NotImplementedError

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
        session: WhatsappSession,
    ):
        raise NotImplementedError
