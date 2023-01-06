import json
from typing import List

from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.whatsapp_text_button import WhatsAppTextButton


class FormattedTemplateMessage:
    def __init__(
        self,
        data,
        template_name,
        image_url=None,
        text=None,
        buttons: List[WhatsAppTextButton] = None,
    ):
        self.messaging_product = "whatsapp"
        self.to = data.get("from_phone_number")
        self.type = "template"
        self.template = {
            "name": template_name,
            "language": {"code": "en"},
        }
        self.components = []
        self.image_url = image_url
        self.text = text
        self.buttons = buttons

    def to_json(self) -> dict:
        json_content = {
            "messaging_product": self.messaging_product,
            "to": self.to,
            "type": self.type,
            "template": self.template,
            "components": self.components,
        }

        if self.image_url:
            json_content["components"].append(
                {
                    "type": "header",
                    "parameters": [
                        {
                            "type": "image",
                            "image": {
                                "url": self.image_url,
                            },
                        }
                    ],
                }
            )

        if self.text:
            json_content["components"].append(
                {
                    "type": "body",
                    "parameters": [
                        {
                            "type": "text",
                            "text": self.text,
                        }
                    ],
                }
            )

        if self.buttons:
            for button in self.buttons:
                json_content["components"].append(button.to_json())

        return json_content


class FormattedTextMessage:
    def __init__(self, text: str, phone_number: str):
        self.text = text
        self.phone_number = phone_number

    def to_json(self) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "text",
            "text": {"preview_url": False, "body": self.text},
        }


class FormattedImageMessage:
    def __init__(self, image_url: str, phone_number: str):
        self.image_url = image_url
        self.phone_number = phone_number

    def to_json(self) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "image",
            "image": {"link": self.image_url},
        }


class FormattedInteractiveMessage:
    def __init__(
        self,
        header_text: str,
        text: str,
        phone_number: str,
        rows: List[InteractiveRow],
        section_text: str = "Menu Options",
    ):
        self.header_text = header_text
        self.text = text
        self.phone_number = phone_number
        self.rows = rows
        self.section_text = section_text

    def to_json(self) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": self.header_text},
                "body": {"text": self.text},
                "action": {
                    "button": "Tregers Menu",
                    "sections": [
                        {
                            "title": self.section_text,
                            "rows": [row.to_json() for row in self.rows],
                        }
                    ],
                },
            },
        }
