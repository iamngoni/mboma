import json
import re
from io import BytesIO

import requests
from decouple import config
from django.core.files.uploadedfile import InMemoryUploadedFile

from bot.models import WhatsappSession
from services.helpers.utils import Utils
from users.models import User
from loguru import logger


class WhatsappService:
    def __init__(self, formatted_message: dict, user_status: bool, user=None):
        self.formatted_message = formatted_message
        self.user_status = user_status
        self.user = user
        self.full_name = user.first_name if user else None
        self.client = (
            User.get_user_by_phone_number(self.formatted_message["from_phone_number"])
            if user
            else None
        )

    def process(self):
        if self.user_status:
            if self.formatted_message["message_type"] == "button":
                # process button message
                return self.process_button_message()

            elif self.formatted_message["message_type"] == "text":
                # process text message
                return self.process_text_message()

            elif self.formatted_message["message_type"] == "interactive":
                # process interactive message
                return self.process_interactive_message()

            elif self.formatted_message["message_type"] == "document":
                # process document message
                return self.process_document_message()

            elif self.formatted_message["message_type"] == "image":
                # process image message
                return self.process_image_message()
            else:
                return self.generic_error()
        else:
            user = User.create_user(
                self.formatted_message["from_phone_number"],
                self.formatted_message["from_phone_number"],
                self.formatted_message["whatsapp_name"],
                f'{self.formatted_message["from_phone_number"]}@modestnerd.co',
                self.formatted_message["from_phone_number"],
                "CUSTOMER",
                "bot",
            )
            if user:
                user.has_session = True
                user.save()
                try:
                    WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                        self.formatted_message["from_phone_number"],
                        "greeting",
                        "greeting",
                        payload={},
                    )
                except Exception as e:
                    print(e)
                return self.greeting_message(self.formatted_message, False)
            else:
                # TODO: send message to user that something went wrong
                return self.generic_error()

    def process_button_message(self):
        session = WhatsappSession.get_whatsapp_session(
            self.formatted_message["from_phone_number"]
        )
        if self.formatted_message["message"] == "Register Now":
            return self.register_user(self.formatted_message)
        elif self.formatted_message["message"].lower() == "faqs":
            payload = Utils.get_faq(self.formatted_message)
            whatsapp = WhatsappMessage(payload=payload)
            return whatsapp.send_message()
        elif self.formatted_message["message"].lower() == "about us":
            payload = Utils.get_about_us(self.formatted_message)
            whatsapp = WhatsappMessage(payload=payload)
            return whatsapp.send_message()

        elif session:
            if session.stage == "menu":
                self.process_menu(session)
            elif session.stage == "registration":
                self.process_registration(session)
            elif session.stage == "uploads":
                self.process_upload(session)
            elif session.stage == "update_info":
                self.process_update_info(session)
            elif session.stage == "browse_jobs":
                self.process_browse_jobs(session)
            elif session.stage == "applications":
                self.process_applications(session)
            else:
                return self.generic_error()
        else:
            return self.generic_error()

    def process_text_message(self):
        if self.formatted_message["message"].lower() in [
            "ndeipi",
            "wadii",
            "zvirisei",
            "madii",
            "menu",
            "back",
            "main menu",
            "home",
            "main",
            "start",
            "hi",
            "hello",
            "hey",
            "hie",
            "hi there",
            "hello there",
            "hey there",
            "hie there",
        ]:
            session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                self.formatted_message["from_phone_number"], "menu", "menu", {}
            )
            if session:
                session.reset_to_menu()
                payload = Utils.get_menu(
                    self.formatted_message,
                    f"Welcome Back, {self.full_name}\n\nFind your next Job with us💼",
                )
                whatsapp = WhatsappMessage(payload=payload)
                return whatsapp.send_message()
            else:
                return self.generic_error()
        else:
            session = WhatsappSession.get_whatsapp_session(
                self.formatted_message["from_phone_number"]
            )
            if session:
                if session.stage == "registration":
                    return self.process_registration(session)
                elif session.stage == "menu":
                    return self.process_menu(session)
                elif session.stage == "uploads":
                    return self.process_upload(session)
                elif session.stage == "update_info":
                    return self.process_update_info(session)
                elif session.stage == "browse_jobs":
                    return self.process_browse_jobs(session)
                elif session.stage == "applications":
                    return self.process_applications(session)
                else:
                    payload = Utils.get_menu(
                        self.formatted_message, f"Welcome Back, {self.full_name}"
                    )
                    whatsapp = WhatsappMessage(payload=payload)
                    return whatsapp.send_message()
            else:
                print("Session not created")
                return self.generic_error()

    def process_interactive_message(self):
        if not self.user.is_registered:
            # check if user is registering
            # if not, register user
            session = WhatsappSession.get_whatsapp_session(
                self.formatted_message["from_phone_number"]
            )
            if session:
                if session.stage == "registration":
                    return self.process_registration(session)
                else:
                    return self.register_user(self.formatted_message)
            print("User not registered")
            session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                self.formatted_message["from_phone_number"], "registration", "name", {}
            )
            if session:
                payload = Utils.get_first_name(self.formatted_message)
                whatsapp = WhatsappMessage(payload=payload)
                return whatsapp.send_message()
            else:
                print("Session not created")
                return self.generic_error()

        type = self.formatted_message["interactive_type"]
        if type == "list_reply":
            # check user stage
            # check user position
            # process list reply
            session = WhatsappSession.get_whatsapp_session(
                self.formatted_message["from_phone_number"]
            )
            if session:
                if session.stage == "menu":
                    self.process_menu(session)
                elif session.stage == "registration":
                    self.process_registration(session)
                elif session.stage == "uploads":
                    self.process_upload(session)
                elif session.stage == "update_info":
                    self.process_update_info(session)
                elif session.stage == "browse_jobs":
                    self.process_browse_jobs(session)
                elif session.stage == "applications":
                    self.process_applications(session)
                else:
                    return self.generic_error()
            else:
                return self.generic_error()
        elif type == "button_reply":
            # check user stage
            # check user position
            # process button reply
            session = WhatsappSession.get_whatsapp_session(
                self.formatted_message["from_phone_number"]
            )
            if session:
                if session.stage == "menu":
                    self.process_menu(session)
                elif session.stage == "registration":
                    self.process_registration(session)
                elif session.stage == "uploads":
                    self.process_upload(session)
                elif session.stage == "update_info":
                    self.process_update_info(session)
                elif session.stage == "browse_jobs":
                    self.process_browse_jobs(session)
                elif session.stage == "applications":
                    self.process_applications(session)
                else:
                    return self.generic_error()
            else:
                return self.generic_error()
        else:
            return self.generic_error()

    def process_document_message(self):
        session = WhatsappSession.get_whatsapp_session(
            self.formatted_message["from_phone_number"]
        )
        if session:
            if session.stage == "uploads":
                self.process_upload(session)
            elif session.stage == "update_info":
                self.process_update_info(session)
            else:
                return self.generic_error()
        else:
            print("Session not created")
            return self.generic_error()

    def process_image_message(self):
        session = WhatsappSession.get_whatsapp_session(
            self.formatted_message["from_phone_number"]
        )
        if session:
            if session.stage == "uploads":
                self.process_upload(session)
            elif session.stage == "update_info":
                self.process_update_info(session)
            else:
                return self.generic_error()
        else:
            print("Session not created")
            return self.generic_error()

    # functions
    def greeting_message(self, formatted_message, status):
        if not status:
            payload = Utils.get_greeting_message(formatted_message)
            whatsapp = WhatsappMessage(payload=payload)
            return whatsapp.send_message()
        else:
            return self.generic_error()

    def generic_error(self):
        payload = Utils.get_invalid_response(self.formatted_message)
        whatsapp = WhatsappMessage(payload=payload)
        return whatsapp.send_message()

    def register_user(self, formatted_message):
        session = WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
            formatted_message["from_phone_number"], "registration", "name", {}
        )
        if session:
            payload = Utils.get_first_name(formatted_message)
            whatsapp = WhatsappMessage(payload=payload)
            return whatsapp.send_message()
        else:
            return self.generic_error()

    def process_menu(self, session):
        try:
            if session.position == "menu":
                if self.user.is_registered:
                    print(">>>>>>", self.formatted_message["list_reply"]["id"])
                    if self.formatted_message["list_reply"]["id"] == "1":
                        session.stage = "uploads"
                        session.position = "document_type"
                        session.save()
                        # document_types = DocumentTypes.objects.all().order_by("id")
                        document_types = []
                        document_types_list = []
                        for document_type in document_types:
                            document_types_list.append(
                                {
                                    "id": document_type.id,
                                    "title": document_type.document_type,
                                    "description": document_type.description,
                                }
                            )
                        payload = Utils.get_document_type_client(
                            self.formatted_message, document_types_list
                        )
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()

                    elif self.formatted_message["list_reply"]["id"] == "2":
                        session.stage = "update_info"
                        session.position = "field"
                        session.save()
                        payload = Utils.get_edit_field(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()
                    elif self.formatted_message["list_reply"]["id"] == "5":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_about_us(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()
                    elif self.formatted_message["list_reply"]["id"] == "6":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_contact_us(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()
                    elif self.formatted_message["list_reply"]["id"] == "7":
                        session.stage = "menu"
                        session.position = "menu"
                        session.save()
                        payload = Utils.get_faq(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()
                    else:
                        return self.generic_error()
                else:
                    print("User not registered")
                    session = (
                        WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                            self.formatted_message["from_phone_number"],
                            "registration",
                            "name",
                            {},
                        )
                    )
                    if session:
                        payload = Utils.get_first_name(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()
                    else:
                        print("Session not created")
                        return self.generic_error()
            else:
                return self.generic_error()
        except Exception as e:
            print(e)
            return self.generic_error()

    def process_registration(self, session):
        try:
            if session.position == "name":
                session.payload["first_name"] = self.formatted_message["message"]
                session.position = "last_name"
                session.save()
                payload = Utils.get_last_name(self.formatted_message)
                whatsapp = WhatsappMessage(payload=payload)
                return whatsapp.send_message()
            elif session.position == "last_name":
                session.position = "email_address"
                session.payload["last_name"] = self.formatted_message["message"]
                session.save()
                payload = Utils.get_email_address(self.formatted_message)
                whatsapp = WhatsappMessage(payload=payload)
                return whatsapp.send_message()
            elif session.position == "email_address":
                # TODO validate email
                email = self.formatted_message["message"]
                if email.lower() == "none":
                    # generate random email based on phone number
                    email = (
                        f"{self.formatted_message['from_phone_number']}@victory.co.zw"
                    )
                else:
                    # validate email
                    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
                    if re.search(regex, email):
                        print("Valid Email")
                    else:
                        print("Invalid Email")
                        payload = Utils.get_invalid_email(self.formatted_message)
                        whatsapp = WhatsappMessage(payload=payload)
                        return whatsapp.send_message()

                session.payload["email_address"] = self.formatted_message["message"]
                session.position = "industry"
                session.save()

                payload = Utils.get_menu(self.formatted_message, self.formatted_message)
                whatsapp = WhatsappMessage(payload=payload)
                return whatsapp.send_message()
            else:
                return self.generic_error()
        except Exception as e:
            print(e)
            return self.generic_error()

    def process_update_info(self, session):
        try:
            if session.position == "field":
                session.payload["field_id"] = self.formatted_message["list_reply"]["id"]
                session.position = "update"
                session.save()
                if session.payload["field_id"] != "7":
                    payload = Utils.get_generic_update_question(
                        self.formatted_message,
                        f"Please enter the new value to update {self.formatted_message['list_reply']['title']}",
                    )
                    whatsapp = WhatsappMessage(payload=payload)
                    return whatsapp.send_message()
                else:
                    # get profile picture
                    payload = Utils.get_profile_picture(self.formatted_message)
                    whatsapp = WhatsappMessage(payload=payload)
                    return whatsapp.send_message()

            elif session.position == "update":
                if session.payload["field_id"] == "1":
                    field = "Your first name"
                    self.client.first_name = self.formatted_message["message"]
                elif session.payload["field_id"] == "2":
                    field = "Your last name"
                    self.client.last_name = self.formatted_message["message"]
                elif session.payload["field_id"] == "3":
                    field = "Your email address"
                    self.client.email_address = self.formatted_message["message"]
                elif session.payload["field_id"] == "4":
                    field = "Your phone number"
                    self.client.phone_number = self.formatted_message["message"]
                elif session.payload["field_id"] == "5":
                    field = "Your date of birth"
                    self.client.date_of_birth = self.formatted_message["message"]
                elif session.payload["field_id"] == "6":
                    field = "Your address"
                    self.client.address = self.formatted_message["message"]
                elif session.payload["field_id"] == "7":
                    field = "Your Profile picture"
                    # upload document
                    print("file uploaded")
                    # save document
                    headers = {
                        "Authorization": f'Bearer {config("WHATSAPP_TOKEN")}',
                        "Content-Type": "application/json",
                    }
                    file_request = requests.request(
                        "GET",
                        url=f"{config('WHATSAPP_URL')}{self.formatted_message['media_id']}/",
                        headers=headers,
                        data={},
                    )
                    print(">>>>", file_request)
                    print(">>>>", file_request.json())
                    if file_request.status_code == 200:
                        print("file url obtained")
                        # get media url
                        url = file_request.json()["url"]
                        # get file type
                        mime_type = file_request.json()["mime_type"]
                        sha256 = file_request.json()["sha256"]
                        id = file_request.json()["id"]
                        file_size = file_request.json()["file_size"]
                    else:
                        print("file url not obtained")
                        return self.generic_error()
                    # download file
                    payload = {}
                    headers = {"Authorization": f'Bearer {config("WHATSAPP_TOKEN")}'}
                    file = requests.request("GET", url, headers=headers, data=payload)
                    if file.status_code == 200:
                        print("file downloaded")
                        try:
                            # check message type
                            if self.formatted_message["message_type"] == "image":
                                if mime_type == "image/jpeg":
                                    file_name = f"{id}.jpg"
                                elif mime_type == "image/png":
                                    file_name = f"{id}.png"
                                elif mime_type == "image/gif":
                                    file_name = f"{id}.gif"
                                else:
                                    file_name = f"{id}.jpg"
                            if self.formatted_message["message_type"] == "document":
                                file_name = self.formatted_message["document"][
                                    "filename"
                                ]
                            # convert to file on memory
                            bytesio_o = BytesIO(file.content)
                            obj = InMemoryUploadedFile(
                                bytesio_o,
                                None,
                                file_name,
                                mime_type,
                                bytesio_o.getbuffer().nbytes,
                                None,
                            )
                            # save file
                            try:
                                self.client.profile_picture = obj
                            except Exception as e:
                                print("Failed to delete file", e)
                                return self.generic_error()
                        except Exception as e:
                            print("Failed to save file", e)
                            return self.generic_error()
                    else:
                        return self.generic_error()
                elif session.payload["field_id"] == "8":
                    field = "Your passport number"
                    self.client.passport_number = self.formatted_message["message"]
                elif session.payload["field_id"] == "9":
                    field = "Your gender"
                    self.client.gender = self.formatted_message["message"]
                else:
                    return self.generic_error()
                self.client.save()
                show_menu = (
                    WhatsappSession.create_whatsapp_session_or_get_whatsapp_session(
                        self.formatted_message["from_phone_number"], "menu", "menu", {}
                    )
                )
                if show_menu:
                    payload = Utils.get_menu(
                        self.formatted_message, f"{field} updated successfully✅"
                    )
                    whatsapp = WhatsappMessage(payload=payload)
                    return whatsapp.send_message()
                else:
                    return self.generic_error()
            else:
                return self.generic_error()
        except Exception as e:
            logger.error(e)
            return self.generic_error()


class WhatsappMessage:
    def __init__(self, payload: dict):
        self.payload = payload

    def send_message(self):
        headers = {
            "Authorization": f'Bearer {config("WHATSAPP_TOKEN")}',
            "Content-Type": "application/json",
        }
        payload = json.dumps(self.payload)
        print("SENDING TO WHATSAPP PAYLOAD >>", payload)
        response = requests.request(
            "POST",
            f'{config("WHATSAPP_URL")}105156245801398/messages',
            headers=headers,
            data=payload,
        )
        print(response.text)
