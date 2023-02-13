#
#  products_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from typing import Optional

from decouple import config

from bot.models import WhatsappSession
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.messages import InteractiveListMessage, ProductsMessage
from services.whatsapp.product_section import ProductSection
from shop.models import ProductCategory
from loguru import logger


class ProductsDialog(WhatsAppDialog):
    name = "products_dialog"

    def dialog_message(
        self,
        incoming_message: WhatsAppMessageDTO,
        session: WhatsappSession,
    ):
        session.dialog_name = self.name
        session.save()

        # get categories with more than one product
        categories = ProductCategory.objects.exclude(products__isnull=True)
        logger.info(f"Categories with products -> {categories}")

        category_names_concatenated = ""
        for index, category in enumerate(categories):
            category_names_concatenated += (
                f"*{category.name}*{' and' if index == categories.count() - 1 else ','}"
            )

        logger.info(category_names_concatenated)

        return ProductsMessage(
            header_text="Tregers Products",
            text=f"Browse through our {category_names_concatenated} to find what you would like to purchase 😊.",
            phone_number=incoming_message.from_phone_number,
            catalog_id=config("CATALOG_ID"),
            product_sections=[
                ProductSection(title=category.name, products=category.products.all())
                for category in categories
            ],
        )

    def next_dialog(
        self,
        incoming_message: WhatsAppMessageDTO,
        previous_dialog_name: Optional[str],
    ):
        pass
