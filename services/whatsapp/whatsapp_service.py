import re
import time

from loguru import logger

from api.views.bot.tasks import mark_message_as_read
from bot.models import WhatsappSession
from services.dialogs.email_address_dialog import EmailAddressDialog
from services.dialogs.first_name_dialog import FirstNameDialog
from services.dialogs.welcome_dialog import WelcomeDialog
from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.helpers.create_username import create_username
from services.helpers.generate_random_password import generate_random_password
from services.helpers.whatsapp_helpers import WhatsAppHelpers
from services.whatsapp.messages import (
    TextMessage,
    ImageMessage,
)
from services.whatsapp.whatsapp_message import WhatsappMessage
from users.models import User, UserRoles


class WhatsAppService:
    def __init__(self, message: WhatsAppMessageDTO):
        self.incoming_whatsapp_message = message
        self.session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            phone_number=message.from_phone_number
        )
        self.is_registered = User.is_registered(phone_number=message.from_phone_number)

    def process(self):
        """Process incoming Whatsapp Message"""
        # mark incoming message as read
        try:
            logger.info("scheduling job to mark message as read")
            mark_message_as_read.delay(self.incoming_whatsapp_message.id)
            logger.info("job scheduled")

            if self.is_registered:
                logger.info("user is registered")
                if self.incoming_whatsapp_message.message_type == "text":
                    logger.info("processing text message")
                    # process text message
                    return self.process_text_message()
                elif self.incoming_whatsapp_message.message_type == "interactive":
                    logger.info("processing interactive message")
                    # process interactive message
                    return self.process_interactive_message()
                else:
                    logger.error("failed to determine type of message")
                    payload = TextMessage(
                        text="Invalid Response. Try again",
                        phone_number=self.incoming_whatsapp_message.from_phone_number,
                    )

                    message = WhatsappMessage(payload=payload.to_json())
                    message.send()

            else:
                logger.info("user is not registered")
                logger.info("checking if there's a session")
                if self.session and self.session.payload.get("first_name", None):
                    self.process_registration(self.session)
                    return

                self.send_greeting_message()
                self.register_user()
        except Exception as exc:
            logger.error(f"Failed to process incoming message -> {exc}")
            self.send_error_message()
            # self.send_main_menu()
            return

    def process_text_message(self):
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            self.incoming_whatsapp_message.from_phone_number
        )
        if session:
            logger.info("has session")
            if session.stage == "registration":
                logger.info("sending to process registration")
                return self.process_registration(session)
            else:
                logger.info("sending back menu")
                message = WhatsappMessage(
                    payload=WelcomeDialog()
                    .dialog_message(
                        incoming_message=self.incoming_whatsapp_message,
                        session=self.session,
                    )
                    .to_json()
                )
                message.send()
                return
        else:
            logger.error("failed to get or create session")
            self.send_error_message()
            return

    def process_interactive_message(self):
        if self.session:
            logger.info(f"session stage -> {self.session.stage}")
            previous_dialog = WhatsAppHelpers.get_previous_dialog(
                self.session.dialog_name
            )
            next_dialog = previous_dialog.next_dialog(
                incoming_message=self.incoming_whatsapp_message,
                previous_dialog_name=self.session.dialog_name,
            )

            if previous_dialog:
                logger.info(
                    "***transition from dialog : %s to next dialog : %s",
                    previous_dialog.name,
                    next_dialog.name,
                )

            # set the next dialogs recipient phone number
            dialog_message = next_dialog.dialog_message(
                incoming_message=self.incoming_whatsapp_message, session=self.session
            )
            whatsapp_message = WhatsappMessage(payload=dialog_message.to_json())
            whatsapp_message.send()
            return
        else:
            logger.error("failed to get or create session")
            self.send_error_message()
            return

    def send_greeting_message(self):
        image_payload = ImageMessage(
            phone_number=self.incoming_whatsapp_message.from_phone_number,
            image_url="https://www.tregerproducts.com/wp-content/uploads/treger-products-logo.jpg",
        )
        image_message = WhatsappMessage(payload=image_payload.to_json())
        image_message.send()

        # wait for 3 seconds then send the text message
        time.sleep(3)
        payload = TextMessage(
            phone_number=self.incoming_whatsapp_message.from_phone_number,
            text="Welcome to Tregers, we're glad to have you here. Please wait while "
            "we get you started.",
        )
        message = WhatsappMessage(payload=payload.to_json())
        message.send()
        return

    def send_error_message(self, text="An error occurred. Please try again"):
        payload = TextMessage(
            phone_number=self.incoming_whatsapp_message.from_phone_number,
            text=text,
        )
        whatsapp = WhatsappMessage(payload=payload.to_json())
        whatsapp.send()

    def register_user(self):
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            self.incoming_whatsapp_message.from_phone_number,
        )
        if session:
            message = WhatsappMessage(
                payload=FirstNameDialog()
                .dialog_message(
                    incoming_message=self.incoming_whatsapp_message,
                    session=self.session,
                )
                .to_json()
            )
            message.send()
        else:
            self.send_error_message()
            return

    def process_registration(self, session):
        try:

            previous_dialog = WhatsAppHelpers.get_previous_dialog(
                self.incoming_whatsapp_message.previous_dialog_name
            )
            next_dialog = previous_dialog.next_dialog(
                incoming_message=self.incoming_whatsapp_message,
                previous_dialog_name=self.session.dialog_name,
                session=self.session,
            )

            if previous_dialog.name == "first_name_dialog":
                logger.info("saving first name")
                session.payload["first_name"] = self.incoming_whatsapp_message.message
                session.save()

            if previous_dialog.name == "last_name_dialog":
                logger.info("saving last name")
                session.payload["last_name"] = self.incoming_whatsapp_message.message
                session.save()

            if previous_dialog.name == "email_address_dialog":
                logger.info("saving email address")
                email = self.incoming_whatsapp_message.message
                regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
                if re.search(regex, email):
                    logger.info("Valid Email")
                    session.payload["email_address"] = email
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
                        phone_number=self.incoming_whatsapp_message.from_phone_number,
                        role=UserRoles.CUSTOMER,
                        source="bot",
                        password=password,
                    )

                    payload = TextMessage(
                        phone_number=self.incoming_whatsapp_message.from_phone_number,
                        text=f"An account with your details has been successfully created. Your temporary password is "
                        f"*{password}*.\n\nPlease try to remember the password for future use.",
                    )
                    message = WhatsappMessage(payload=payload.to_json())
                    message.send()
                else:
                    next_dialog = EmailAddressDialog()

            dialog_message = next_dialog.dialog_message(
                incoming_message=self.incoming_whatsapp_message, session=self.session
            )
            whatsapp_message = WhatsappMessage(payload=dialog_message.to_json())
            whatsapp_message.send()

        except Exception as exc:
            logger.error(exc)
            self.send_error_message()
            return
