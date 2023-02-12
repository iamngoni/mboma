#
#  whatsapp_message.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.


from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class WhatsAppMessageDTO:
    """WhatsApp Message DTO"""

    to_phone_number: str
    from_phone_number: str
    id: str
    message_type: str
    previous_dialog_name: Optional[str] = None
    whatsapp_name: Optional[str] = None

    # text messages
    message: Optional[str] = None

    # interactive message fields
    interactive_type: Optional[str] = None
    button_reply: Optional[Dict] = None
    list_reply: Optional[Dict] = None
