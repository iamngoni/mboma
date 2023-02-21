#
#  product_categories_dialog.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 14/2/2023.

from typing import Optional

from loguru import logger

from bot.models import WhatsappSession
from services.dialogs.whatsapp_dialog import WhatsAppDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.messages import InteractiveListMessage
from shop.models import ProductCategory


class ProductCategoriesDialog(WhatsAppDialog):
    name = "product_categories_dialog"

    def dialog_message(
        self, incoming_message: WhatsAppMessageDTO, session: WhatsappSession
    ):
        session.dialog_name = self.name
        session.save()

        # get categories with more than one product
        categories = ProductCategory.objects.exclude(products__isnull=True)
        logger.info(f"Categories with products -> {categories}")

        category_names_concatenated = ""
        for index, category in enumerate(categories):
            category_names_concatenated += f"*{category.name}*{' and ' if index == categories.count() - 2 else ', ' if index < categories.count() - 1 else ''}"

        logger.info(category_names_concatenated)

        return InteractiveListMessage(
            text=f"Browse through our {category_names_concatenated} to find what you would like to purchase 😊.",
            header_text="Product Categories",
            phone_number=incoming_message.from_phone_number,
            rows=[
                InteractiveRow(
                    id=category.id, title=category.name, description=category.name
                )
                for category in categories
            ],
            section_text="Product Categories",
        )

    def next_dialog(
        self, incoming_message: WhatsAppMessageDTO, previous_dialog_name: Optional[str]
    ):
        from services.dialogs.catalog_products_dialog import CatalogProductsDialog

        return CatalogProductsDialog()
