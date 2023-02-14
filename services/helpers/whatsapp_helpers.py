#
#  whatsapp_helpers.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.
from services.dialogs.catalog_products_dialog import CatalogProductsDialog
from services.dialogs.confirm_order_dialog import ConfirmOrderDialog
from services.dialogs.email_address_dialog import EmailAddressDialog
from services.dialogs.first_name_dialog import FirstNameDialog
from services.dialogs.go_to_checkout_dialog import GoToCheckoutDialog
from services.dialogs.how_it_works_dialog import HowItWorksDialog
from services.dialogs.last_name_dialog import LastNameDialog
from services.dialogs.my_account_dialog import MyAccountDialog
from services.dialogs.my_orders_dialog import MyOrdersDialog
from services.dialogs.payment_dialog import PaymentDialog
from services.dialogs.payment_method_dialog import PaymentMethodDialog
from services.dialogs.phone_number_question_dialog import PhoneNumberQuestionDialog
from services.dialogs.product_categories_dialog import ProductCategoriesDialog
from services.dialogs.product_dialog import ProductDialog
from services.dialogs.product_quantity_dialog import ProductQuantityDialog
from services.dialogs.products_dialog import ProductsDialog
from services.dialogs.welcome_dialog import WelcomeDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from loguru import logger


class WhatsAppHelpers:
    @staticmethod
    def requires_system_action(incoming_whatsapp_message: dict) -> bool:
        """
        Check if incoming whatsapp request has messages in the body
        """
        if incoming_whatsapp_message["entry"][0]["changes"][0]["value"].get("messages"):
            return True
        return False

    @staticmethod
    def format_message(incoming_whatsapp_message: dict) -> WhatsAppMessageDTO:
        # common fields across all messages
        try:
            message_data = {
                "to_phone_number": incoming_whatsapp_message.get("to"),
                "from_phone_number": incoming_whatsapp_message["entry"][0]["changes"][
                    0
                ]["value"]["messages"][0]["from"],
                "id": incoming_whatsapp_message["entry"][0]["changes"][0]["value"][
                    "messages"
                ][0]["id"],
                "whatsapp_name": incoming_whatsapp_message["entry"][0]["changes"][0][
                    "value"
                ]["contacts"][0]["profile"]["name"],
                "message_type": incoming_whatsapp_message["entry"][0]["changes"][0][
                    "value"
                ]["messages"][0]["type"],
            }

            # extract data based on type of message
            if message_data["message_type"] == "text":
                message_data["message"] = incoming_whatsapp_message["entry"][0][
                    "changes"
                ][0]["value"]["messages"][0]["text"]["body"]

            if message_data["message_type"] == "button":
                message_data["message"] = incoming_whatsapp_message["entry"][0][
                    "changes"
                ][0]["value"]["messages"][0]["button"]["text"]

            if message_data["message_type"] == "interactive":
                message_data["interactive_type"] = incoming_whatsapp_message["entry"][
                    0
                ]["changes"][0]["value"]["messages"][0]["interactive"]["type"]
                if message_data["interactive_type"] == "button_reply":
                    message_data["button_reply"] = incoming_whatsapp_message["entry"][
                        0
                    ]["changes"][0]["value"]["messages"][0]["interactive"][
                        "button_reply"
                    ]

                if message_data["interactive_type"] == "list_reply":
                    message_data["list_reply"] = incoming_whatsapp_message["entry"][0][
                        "changes"
                    ][0]["value"]["messages"][0]["interactive"]["list_reply"]

            message = WhatsAppMessageDTO(**message_data)
            return message
        except Exception as exc:
            logger.error(exc)
            raise

    @staticmethod
    def available_dialogs() -> dict:
        return {
            "welcome_dialog": WelcomeDialog(),
            "how_it_works_dialog": HowItWorksDialog(),
            "products_dialog": ProductsDialog(),
            "my_account_dialog": MyAccountDialog(),
            "first_name_dialog": FirstNameDialog(),
            "last_name_dialog": LastNameDialog(),
            "email_address_dialog": EmailAddressDialog(),
            "my_orders_dialog": MyOrdersDialog(),
            "product_categories_dialog": ProductCategoriesDialog(),
            "catalog_products_dialog": CatalogProductsDialog(),
            "product_dialog": ProductDialog(),
            "product_quantity_dialog": ProductQuantityDialog(),
            "go_to_checkout_dialog": GoToCheckoutDialog(),
            "confirm_order_dialog": ConfirmOrderDialog(),
            "payment_method_dialog": PaymentMethodDialog(),
            "phone_number_question_dialog": PhoneNumberQuestionDialog(),
            "payment_dialog": PaymentDialog(),
        }

    @staticmethod
    def get_previous_dialog(previous_dialog: str):
        """Get previous dialog"""
        if not previous_dialog:
            return WelcomeDialog()
        else:
            try:
                previous_dialog = WhatsAppHelpers.available_dialogs()[previous_dialog]
                return previous_dialog
            except KeyError:
                logger.error(
                    "Requested dialog %s not registered in the dialog registry",
                    previous_dialog,
                )
