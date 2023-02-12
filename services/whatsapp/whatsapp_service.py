import re

from loguru import logger

from api.views.bot.tasks import mark_message_as_read
from bot.models import WhatsappSession
from services.helpers.create_username import create_username
from services.helpers.generate_random_password import generate_random_password
from services.helpers.utils import Utils
from services.whatsapp.interactive_row import InteractiveRow
from services.whatsapp.messages import (
    FormattedTextMessage,
    FormattedInteractiveMessage,
    FormattedImageMessage,
    FormattedProductsMessage,
)
from services.whatsapp.whatsapp_message import WhatsappMessage
from shop.models import Product, ProductCategory
from users.models import User, UserRoles
from decouple import config


class WhatsappService:
    def __init__(self, formatted_message: dict, is_registered: bool, user: User = None):
        self.formatted_message = formatted_message
        self.is_registered = is_registered
        self.user = user
        self.full_name = user.first_name if user else None
        self.client = (
            User.get_user_by_phone_number(self.formatted_message["from_phone_number"])
            if user
            else None
        )

    def process(self):
        # mark incoming message as read
        try:
            logger.info("scheduling job to mark message as read")
            mark_message_as_read.delay(self.formatted_message.get("message_id"))
            logger.info("job scheduled")

            if self.is_registered:
                logger.info("user is registered")
                if self.formatted_message["message_type"] == "text":
                    logger.info("processing text message")
                    # process text message
                    return self.process_text_message()
                elif self.formatted_message["message_type"] == "interactive":
                    logger.info("processing interactive message")
                    # process interactive message
                    return self.process_interactive_message()
                else:
                    logger.error("failed to determine type of message")
                    payload = FormattedTextMessage(
                        text="Invalid Response. Try again",
                        phone_number=self.formatted_message.get("from_phone_number"),
                    )
                    message = WhatsappMessage(payload=payload.to_json())
                    message.send()
            else:
                logger.info("user is not registered")
                logger.info("checking if there's a session")
                session = WhatsappSession.get_whatsapp_session(
                    self.formatted_message.get("from_phone_number")
                )
                if session and session.stage == "registration":
                    self.process_registration(session)
                    return

                self.send_greeting_message()
                self.register_user()
        except Exception as exc:
            logger.error(f"Failed to process incoming message -> {exc}")
            return

    def process_text_message(self):
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            self.formatted_message["from_phone_number"], "menu", "menu", {}
        )
        if session:
            logger.info("has session")
            if session.stage == "registration":
                logger.info("sending to process registration")
                return self.process_registration(session)
            elif session.stage == "menu":
                logger.info("sending to process menu")
                return self.process_menu(session)
            else:
                logger.info("sending back menu")
                payload = Utils.get_menu(
                    self.formatted_message, f"Welcome Back, {self.full_name}"
                )
                message = WhatsappMessage(payload=payload)
                message.send()
                return
        else:
            logger.error("failed to get or create session")
            self.send_error_message()
            return

    def process_interactive_message(self):
        session = WhatsappSession.get_whatsapp_session(
            self.formatted_message["from_phone_number"]
        )
        if session:
            logger.info("session found")
            logger.info(f"session stage -> {session.stage}")
            if session.stage == "menu":
                logger.info("processing menu")
                self.process_menu(session)
                return
            elif session.stage == "products":
                if session.position == "categories":
                    self.process_products_categories_menu(session)
                    return
            else:
                logger.error("stage not found")
                payload = FormattedTextMessage(
                    phone_number=self.formatted_message.get("from_phone_number"),
                    text="Session probably expired. Please try again",
                )
                message = WhatsappMessage(payload=payload.to_json())
                message.send()

                # send menu
                self.send_main_menu()
                return
        else:
            logger.error("failed to get or create session")
            self.send_error_message()
            return

    def send_main_menu(self):
        # get session and set position and stage to menu
        session = WhatsappSession.get_whatsapp_session(
            self.formatted_message.get("from_phone_number")
        )
        session.position = "menu"
        session.stage = "menu"
        session.save()

        payload = self.get_shop_menu_payload()
        message = WhatsappMessage(payload=payload.to_json())
        message.send()
        return

    def get_shop_menu_payload(self) -> FormattedInteractiveMessage:
        return FormattedInteractiveMessage(
            header_text="Welcome to Tregers Pvt Ltd",
            text="Hi 👋🏿 I'm Mboma, Tregers' Quick Response Service. How can I help you?",
            phone_number=self.formatted_message.get("from_phone_number"),
            rows=[
                InteractiveRow(
                    id=1,
                    title="🔩Products",
                    description="View All Products",
                ),
                InteractiveRow(
                    id=2,
                    title="🔎Search For Product",
                    description="Search For A Specific Product",
                ),
                InteractiveRow(
                    id=3,
                    title="🧾My Orders",
                    description="Show All Previous Orders",
                ),
                InteractiveRow(
                    id=4,
                    title="🛒My Cart",
                    description="Show All Items In Cart",
                ),
                InteractiveRow(
                    id=5,
                    title="👨🏿‍💼My Account",
                    description="View Account Details",
                ),
            ],
        )

    def send_greeting_message(self):
        image_payload = FormattedImageMessage(
            phone_number=self.formatted_message.get("from_phone_number"),
            image_url="https://www.tregerproducts.com/wp-content/uploads/treger-products-logo.jpg",
        )
        image_message = WhatsappMessage(payload=image_payload.to_json())
        image_message.send()

        payload = FormattedTextMessage(
            phone_number=self.formatted_message.get("from_phone_number"),
            text="Welcome to Tregers, we're glad to have you here. Please wait while "
            "we get you started",
        )
        message = WhatsappMessage(payload=payload.to_json())
        message.send()
        return

    def send_error_message(self, text="An error occurred. Please try again"):
        payload = FormattedTextMessage(
            phone_number=self.formatted_message.get("from_phone_number"),
            text=text,
        )
        whatsapp = WhatsappMessage(payload=payload.to_json())
        whatsapp.send()

    def register_user(self):
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            self.formatted_message.get("from_phone_number"), "registration", "name", {}
        )
        if session:
            payload = FormattedTextMessage(
                text="Lets get to know each other, please enter your first name...",
                phone_number=self.formatted_message.get("from_phone_number"),
            )
            message = WhatsappMessage(payload=payload.to_json())
            message.send()
        else:
            self.send_error_message()
            return

    def process_menu(self, session):
        try:
            if session.position == "menu":
                logger.info(f"session position -> {session.position}")
                if self.is_registered:
                    menu_item_id = self.formatted_message["list_reply"]["id"]
                    if menu_item_id == "1":
                        session.stage = "products"
                        session.position = "categories"
                        session.save()

                        # get categories with more than one product
                        categories = ProductCategory.objects.exclude(
                            products__isnull=True
                        )
                        logger.info(f"Categories with products -> {categories}")

                        logger.info("creating rows for categories menu")
                        rows = [
                            InteractiveRow(
                                id=index,
                                title=category.name,
                                description=category.description,
                            )
                            for index, category in enumerate(categories)
                        ]
                        logger.info("Created rows for menu")
                        logger.info(f"Current session to update -> {session}")
                        if session.payload is None:
                            session.payload = {}
                            session.save()

                        session.payload["categories"] = [row.to_json() for row in rows]
                        session.save()
                        logger.info("saved categories in session payload")
                        logger.info("generating payload for categories menu")
                        payload = FormattedInteractiveMessage(
                            header_text="Tregers Products",
                            text="Choose Product Category To Retrieve Products",
                            phone_number=self.formatted_message.get(
                                "from_phone_number"
                            ),
                            section_text="Product Categories",
                            rows=rows,
                        )
                        logger.info("payload generated")
                        logger.info("sending payload")
                        message = WhatsappMessage(payload=payload.to_json())
                        message.send()
                        return

                    elif self.formatted_message["list_reply"]["id"] == "2":
                        session.stage = "update_info"
                        session.position = "field"
                        session.save()
                        payload = Utils.get_edit_field(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send()
                    elif self.formatted_message["list_reply"]["id"] == "5":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_about_us(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send()
                    elif self.formatted_message["list_reply"]["id"] == "6":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_contact_us(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send()
                    elif self.formatted_message["list_reply"]["id"] == "7":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_faq(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send()
                    else:
                        return self.send_error_message()
                else:
                    logger.info("User not registered")
                    session = (
                        WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                            self.formatted_message["from_phone_number"],
                            "registration",
                            "name",
                            {},
                        )
                    )
                    if session:
                        self.register_user()
                        return
                    else:
                        logger.error("Session not created")
                        return self.send_error_message()
            else:
                logger.error("Invalid session position")
                self.send_error_message()
                return
        except Exception as exc:
            logger.error(f"Error processing menu -> {exc}")
            self.send_error_message(
                text="Failed to process menu option. Please try again"
            )
            self.send_main_menu()
            return

    def process_products_categories_menu(self, session):
        try:
            menu_item_id = self.formatted_message["list_reply"]["id"]
            logger.info(f"Menu item id -> {menu_item_id}")
            categories = session.payload.get("categories")
            logger.info(f"Categories in session -> {categories}")
            # TODO: this might result in index error so watch out
            filtered_categories = list(
                filter(lambda ct: int(ct.get("id")) == int(menu_item_id), categories)
            )
            logger.info(f"Filtered Categories -> {filtered_categories}")
            category = filtered_categories[0] if len(filtered_categories) > 0 else None
            products = Product.objects.filter(category__name=category.get("title"))
            logger.info(f"Products -> {products}")

            session.stage = "products"
            session.position = "products"
            session.payload["products"] = [{"id": product.id} for product in products]
            session.save()

            payload = FormattedProductsMessage(
                header_text=f"{category.get('title')} Products",
                text="Choose Product To Retrieve More Information",
                phone_number=self.formatted_message.get("from_phone_number"),
                section_title="Products",
                catalog_id=config("CATALOG_ID"),
                products=products,
            )

            message = WhatsappMessage(payload=payload.to_json())
            message.send()
            return

        except Exception as exc:
            logger.error(f"Error processing menu -> {exc}")
            self.send_error_message()
            self.send_main_menu()
            return

    def process_registration(self, session):
        try:
            if session.position == "name":
                session.payload["first_name"] = self.formatted_message["message"]
                session.position = "last_name"
                session.save()
                payload = FormattedTextMessage(
                    text="Please enter your last name...",
                    phone_number=self.formatted_message.get("from_phone_number"),
                )
                message = WhatsappMessage(payload=payload.to_json())
                message.send()
                return
            elif session.position == "last_name":
                session.position = "email_address"
                session.payload["last_name"] = self.formatted_message["message"]
                session.save()
                payload = FormattedTextMessage(
                    text="For communication and information updates enter your email address\nIf you do not have an "
                    "email enter _*None*_\n\nPlease note that your email address will not be shared with any "
                    "third party...",
                    phone_number=self.formatted_message.get("from_phone_number"),
                )
                message = WhatsappMessage(payload=payload.to_json())
                message.send()
                return
            elif session.position == "email_address":
                email = self.formatted_message["message"]
                if email.lower() == "none":
                    # generate random email based on phone number
                    email = f"{self.formatted_message['from_phone_number']}@mboma.modestnerd.co"
                else:
                    # validate email
                    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
                    if re.search(regex, email):
                        logger.info("Valid Email")
                    else:
                        logger.error("Invalid Email")
                        payload = FormattedTextMessage(
                            text="🙁*Invalid*\n\nSorry your email address is invalid, please try again or enter "
                            "_*None*_..",
                            phone_number=self.formatted_message.get(
                                "from_phone_number"
                            ),
                        )
                        message = WhatsappMessage(payload=payload.to_json())
                        message.send()
                        return

                session.payload["email_address"] = self.formatted_message["message"]
                session.stage = "menu"
                session.position = "menu"
                session.save()

                # generate password
                password = generate_random_password()

                # generate username
                username = create_username(
                    first_name=session.payload.get("first_name"),
                    last_name=session.payload.get("last_name"),
                )

                # create user using details saved in session object
                User.create_user(
                    username=username,
                    first_name=session.payload.get("first_name"),
                    last_name=session.payload.get("last_name"),
                    email=session.payload.get("email_address"),
                    phone_number=self.formatted_message.get("from_phone_number"),
                    role=UserRoles.CUSTOMER,
                    source="bot",
                    password=password,
                )

                # notify user that account has been created successfully
                payload = FormattedTextMessage(
                    phone_number=self.formatted_message.get("from_phone_number"),
                    text=f"An account with your details has been successfully created. Your temporary password is "
                    f"*{password}*.\n\nPlease try to remember the password for future use.",
                )
                message = WhatsappMessage(payload=payload.to_json())
                message.send()

                payload = self.get_shop_menu_payload()
                message = WhatsappMessage(payload=payload.to_json())
                message.send()
                return
            else:
                self.send_error_message()
                return
        except Exception as exc:
            logger.error(exc)
            self.send_error_message()
            return

    # def process_update_info(self, session):
    #     try:
    #         if session.position == "field":
    #             session.payload["field_id"] = self.formatted_message["list_reply"]["id"]
    #             session.position = "update"
    #             session.save()
    #             if session.payload["field_id"] != "7":
    #                 payload = Utils.get_generic_update_question(
    #                     self.formatted_message,
    #                     f"Please enter the new value to update {self.formatted_message['list_reply']['title']}",
    #                 )
    #                 whatsapp = WhatsappMessage(payload=payload)
    #                 return whatsapp.send()
    #             else:
    #                 # get profile picture
    #                 payload = Utils.get_profile_picture(self.formatted_message)
    #                 whatsapp = WhatsappMessage(payload=payload)
    #                 return whatsapp.send()
    #
    #         elif session.position == "update":
    #             if session.payload["field_id"] == "1":
    #                 field = "Your first name"
    #                 self.client.first_name = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "2":
    #                 field = "Your last name"
    #                 self.client.last_name = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "3":
    #                 field = "Your email address"
    #                 self.client.email_address = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "4":
    #                 field = "Your phone number"
    #                 self.client.phone_number = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "5":
    #                 field = "Your date of birth"
    #                 self.client.date_of_birth = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "6":
    #                 field = "Your address"
    #                 self.client.address = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "7":
    #                 field = "Your Profile picture"
    #                 # upload document
    #                 print("file uploaded")
    #                 # save document
    #                 headers = {
    #                     "Authorization": f'Bearer {config("WHATSAPP_TOKEN")}',
    #                     "Content-Type": "application/json",
    #                 }
    #                 file_request = requests.request(
    #                     "GET",
    #                     url=f"{config('WHATSAPP_URL')}{self.formatted_message['media_id']}/",
    #                     headers=headers,
    #                     data={},
    #                 )
    #                 print(">>>>", file_request)
    #                 print(">>>>", file_request.json())
    #                 if file_request.status_code == 200:
    #                     print("file url obtained")
    #                     # get media url
    #                     url = file_request.json()["url"]
    #                     # get file type
    #                     mime_type = file_request.json()["mime_type"]
    #                     sha256 = file_request.json()["sha256"]
    #                     id = file_request.json()["id"]
    #                     file_size = file_request.json()["file_size"]
    #                 else:
    #                     print("file url not obtained")
    #                     return self.send_error_message()
    #                 # download file
    #                 payload = {}
    #                 headers = {"Authorization": f'Bearer {config("WHATSAPP_TOKEN")}'}
    #                 file = requests.request("GET", url, headers=headers, data=payload)
    #                 if file.status_code == 200:
    #                     print("file downloaded")
    #                     try:
    #                         # check message type
    #                         if self.formatted_message["message_type"] == "image":
    #                             if mime_type == "image/jpeg":
    #                                 file_name = f"{id}.jpg"
    #                             elif mime_type == "image/png":
    #                                 file_name = f"{id}.png"
    #                             elif mime_type == "image/gif":
    #                                 file_name = f"{id}.gif"
    #                             else:
    #                                 file_name = f"{id}.jpg"
    #                         if self.formatted_message["message_type"] == "document":
    #                             file_name = self.formatted_message["document"][
    #                                 "filename"
    #                             ]
    #                         # convert to file on memory
    #                         bytesio_o = BytesIO(file.content)
    #                         obj = InMemoryUploadedFile(
    #                             bytesio_o,
    #                             None,
    #                             file_name,
    #                             mime_type,
    #                             bytesio_o.getbuffer().nbytes,
    #                             None,
    #                         )
    #                         # save file
    #                         try:
    #                             self.client.profile_picture = obj
    #                         except Exception as e:
    #                             print("Failed to delete file", e)
    #                             return self.send_error_message()
    #                     except Exception as e:
    #                         print("Failed to save file", e)
    #                         return self.send_error_message()
    #                 else:
    #                     return self.send_error_message()
    #             elif session.payload["field_id"] == "8":
    #                 field = "Your passport number"
    #                 self.client.passport_number = self.formatted_message["message"]
    #             elif session.payload["field_id"] == "9":
    #                 field = "Your gender"
    #                 self.client.gender = self.formatted_message["message"]
    #             else:
    #                 return self.send_error_message()
    #             self.client.save()
    #             show_menu = (
    #                 WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
    #                     self.formatted_message["from_phone_number"], "menu", "menu", {}
    #                 )
    #             )
    #             if show_menu:
    #                 payload = Utils.get_menu(
    #                     self.formatted_message, f"{field} updated successfully✅"
    #                 )
    #                 message = WhatsappMessage(payload=payload)
    #                 message.send()
    #                 return
    #             else:
    #                 return self.send_error_message()
    #         else:
    #             return self.send_error_message()
    #     except Exception as e:
    #         logger.error(e)
    #         return self.send_error_message()
