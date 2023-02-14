from typing import List

from loguru import logger

from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.product_section import ProductSection
from services.whatsapp.reply_button import ReplyButton
from services.whatsapp.whatsapp_text_button import WhatsAppTextButton


class TemplateMessage:
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


class TextMessage:
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


class ImageMessage:
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


class InteractiveListMessage:
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
                    "button": self.section_text,
                    "sections": [
                        {
                            "title": "Options",
                            "rows": [row.to_json() for row in self.rows],
                        }
                    ],
                },
            },
        }


class InteractiveButtonMessage:
    def __init__(
        self,
        text: str,
        phone_number: str,
        buttons: List[ReplyButton],
    ):
        self.text = text
        self.phone_number = phone_number
        self.buttons = buttons

    def to_json(self) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": self.text},
                "action": {
                    "buttons": [button.to_json() for button in self.buttons],
                },
            },
        }


class ProductsMessage:
    def __init__(
        self,
        header_text: str,
        text: str,
        phone_number: str,
        catalog_id: str,
        product_sections: List[ProductSection] = [],
    ):
        self.header_text = header_text
        self.text = text
        self.phone_number = phone_number
        self.catalog_id = catalog_id
        self.product_sections = product_sections

    def to_json(self) -> dict:
        logger.info(self.catalog_id)
        logger.info(self.product_sections)
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "interactive",
            "interactive": {
                "type": "product_list",
                "header": {
                    "type": "text",
                    "text": self.header_text,
                },
                "body": {
                    "text": self.text,
                },
                "footer": {
                    "text": "You may browse and shop right here on WhatsApp!",
                },
                "action": {
                    "catalog_id": self.catalog_id,
                    "sections": [
                        {
                            "title": section.title,
                            "product_items": [
                                {"product_retailer_id": product.id}
                                for product in section.products
                            ],
                        }
                        for section in self.product_sections
                    ],
                },
            },
        }


class ReactionMessage:
    def __init__(
        self,
        phone_number: str,
        message_id: str,
    ):
        self.phone_number = phone_number
        self.message_id = message_id

    def to_json(self) -> dict:
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": self.phone_number,
            "type": "reaction",
            "reaction": {"message_id": self.message_id, "emoji": "👀"},
        }
