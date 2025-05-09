#
#  product_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

import time
from typing import Optional

from decouple import config
from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.product_quantity_dialog import ProductQuantityDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import (
    TextMessage,
    ImageMessage,
    InteractiveProductButtonsMessage,
    InteractiveButtonMessage,
)
from services.whatsapp.reply_button import ReplyButton
from services.whatsapp.whatsapp_message import WhatsappMessage
from shop.models import Product


class ProductDialog(WhatsAppDialog):
    name = "product_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        input_id = incoming_message.list_reply.get("id")
        if input_id:
            try:
                product = Product.objects.get(id=input_id)
                session.payload["product_id"] = product.id
                session.save()

                # send product image
                image_message = ImageMessage(
                    image_url=f"{config('ORIGIN')}{product.image.url}",
                    phone_number=incoming_message.from_phone_number,
                )
                message = WhatsappMessage(payload=image_message.to_json())
                message.send()

                # wait for image to be sent
                time.sleep(1)

                return InteractiveButtonMessage(
                    phone_number=incoming_message.from_phone_number,
                    text=f"*🛍️ {product.name}*\n\n**Description**\n{product.description}\n\nAvailable: "
                    f"{product.inventory.quantity}\nPrice: *${product.price}*",
                    buttons=[
                        ReplyButton(button_id="add_to_cart", title="🛒Add To Cart"),
                        ReplyButton(
                            button_id="back_to_categories", title="⏮️Categories"
                        ),
                    ],
                )

            except Product.DoesNotExist:
                return TextMessage(
                    phone_number=incoming_message.from_phone_number,
                    text="Product is no longer available",
                )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number, text="Invalid input."
            )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        if incoming_message.button_reply:
            option_selected = incoming_message.button_reply.get("id")

            if option_selected == "add_to_cart":
                return ProductQuantityDialog()

            if option_selected == "back_to_categories":
                from services.dialogs.product_categories_dialog import (
                    ProductCategoriesDialog,
                )

                return ProductCategoriesDialog()
        else:
            logger.error("panic! weird response")
            return self
