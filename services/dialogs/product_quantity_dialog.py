#
#  product_quantity_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

import math
from typing import Optional

from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.go_to_checkout_dialog import GoToCheckoutDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.messages import TextMessage, InteractiveListMessage
from services.whatsapp.whatsapp_message import WhatsappMessage
from shop.models import Product, Cart
from users.models import User


class ProductQuantityDialog(WhatsAppDialog):
    name = "product_quantity_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        product = Product.objects.get(id=session.payload.get("product_id"))
        step = 1
        inventory_range = product.inventory.quantity + 1
        if inventory_range > 10:
            inventory_range_div_10 = inventory_range / 10
            logger.info(inventory_range_div_10)
            # get the floor value of inventory_range_div_10
            step = math.ceil(inventory_range_div_10)
            logger.info(f"Using {step} as step value instead of 1")

        return InteractiveListMessage(
            phone_number=incoming_message.from_phone_number,
            text=f"Please enter quantity for *{product.name}* (max: {product.inventory.quantity})",
            header_text="Available Quantities",
            section_text="Available Quantities",
            rows=[
                InteractiveRow(
                    id=f"{number}", title=f"{number}", description=f"{number} item(s)"
                )
                for number in range(0, inventory_range, step)
            ],
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        input_id = incoming_message.list_reply.get("id")
        if input_id:
            user = User.get_user_by_phone_number(incoming_message.from_phone_number)
            if user:
                session = WhatsappSession.objects.get(
                    phone_number=incoming_message.from_phone_number
                )
                product = Product.objects.get(id=session.payload.get("product_id"))
                cart = Cart.create_cart_or_get_cart(user)
                cart_item = cart.add_cart_item_or_create_cart_item(
                    product, int(input_id)
                )
                logger.info(cart_item)

                text_message = TextMessage(
                    phone_number=incoming_message.from_phone_number,
                    text=f"{int(input_id)} x {product.name} added to cart ✅",
                )
                WhatsappMessage(text_message.to_json()).send()

                return GoToCheckoutDialog()
            else:
                logger.error("panic!!! no user")
        else:
            logger.error("panic!! aahh no input")
