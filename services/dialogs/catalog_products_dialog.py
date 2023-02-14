#
#  catalog_products_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.
from typing import Optional

from bot.models import WhatsappSession
from services.dialogs.product_dialog import ProductDialog
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.messages import TextMessage, InteractiveListMessage
from shop.models import ProductCategory


class CatalogProductsDialog(WhatsAppDialog):
    name = "catalog_products_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        input_id = incoming_message.list_reply.get("id")
        if input_id:
            try:
                category = ProductCategory.objects.get(id=input_id)
                products = category.products.filter(inventory__quantity__gt=0)
                if products.count() > 0:
                    return InteractiveListMessage(
                        text=f"Browse through our *{category.name} Products* to find what you would like to purchase 😊.",
                        header_text=f"{category.name} Products",
                        phone_number=incoming_message.from_phone_number,
                        rows=[
                            InteractiveRow(
                                id=product.id,
                                title=product.name[:24],
                                description=product.name,
                            )
                            for product in products
                        ],
                        section_text=category.name,
                    )
                else:
                    return TextMessage(
                        phone_number=incoming_message.from_phone_number,
                        text="Chosen category has no valid products",
                    )
            except ProductCategory.DoesNotExist:
                return TextMessage(
                    phone_number=incoming_message.from_phone_number,
                    text="Category not found",
                )
        else:
            return TextMessage(
                phone_number=incoming_message.from_phone_number, text="Invalid input."
            )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        return ProductDialog()
