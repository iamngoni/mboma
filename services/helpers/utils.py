import datetime
from decouple import config


class Utils:
    def __init__(self):
        pass

    def get_coming_soon(self, data):
        return Utils.generic_message(
            self,
            data,
            "🙁*Apologies*\n\nThis feature is coming soon...",
        )

    def get_invalid_response(self, data):
        return Utils.generic_message(
            self,
            data,
            "🙁*Invalid*\n\nSorry i could not understand your response, say _*hie*_ to start "
            "afresh",
        )

    def get_invalid_email(self, data):
        return Utils.generic_message(
            self,
            data,
            "🙁*Invalid*\n\nSorry your email address is invalid, please try again or enter _*None*_...",
        )

    def get_not_registered(self, data):
        return Utils.generic_message(
            self,
            data,
            "You are not registered, please register first\n\nLets get to know each other, please enter your first "
            "name...",
        )

    def get_generic_update_question(self, data, message):
        return Utils.generic_message(self, data, message)

    def get_first_name(self, data):
        return Utils.generic_message(
            self,
            data,
            "Lets get to know each other, please enter your first name...",
        )

    def get_last_name(self, data):
        return Utils.generic_message(self, data, "Please enter your last name...")

    def get_email_address(self, data):
        return Utils.generic_message(
            self,
            data,
            "For communication and information updates enter your email address\nIf you do not have an email enter _*None*_\n\nPlease note that your email address will not be shared with any third party...",
        )

    def get_successful_registration(self, data):
        return Utils.generic_message(
            self, data, "Thank you for registering with Victory Milestone\n\n"
        )

    def get_profile_picture(self, data):
        return Utils.generic_message(
            self, data, "Please select a picture of yourself..."
        )

    def get_greeting_message(self, data):
        return {
            "messaging_product": "whatsapp",
            "to": data["from_phone_number"],
            "type": "template",
            "template": {
                "name": "greeting",
                "language": {"code": "en"},
                "components": [
                    {
                        "type": "header",
                        "parameters": [
                            {
                                "type": "image",
                                "image": {"link": config("WHATSAPP_GREETING_IMAGE")},
                            }
                        ],
                    },
                    {
                        "type": "body",
                        "parameters": [
                            {
                                "type": "text",
                                "text": "Morning"
                                if datetime.datetime.now().hour < 12
                                else "Afternoon",
                            },
                            {"type": "text", "text": data["whatsapp_name"]},
                        ],
                    },
                    {
                        "type": "button",
                        "sub_type": "quick_reply",
                        "index": 0,
                        "parameters": [{"type": "text", "text": "Yes"}],
                    },
                    {
                        "type": "button",
                        "sub_type": "quick_reply",
                        "index": 1,
                        "parameters": [{"type": "text", "text": "No"}],
                    },
                ],
            },
        }

    def generic_message(self, data, message):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "text",
            "text": {
                "body": message,
            },
        }

    def get_menu(self, data, message):
        body = """What would you like to do next?"""
        return Utils.get_menu_action(self, data, message, body)

    def get_about_us(self, data):
        message = "📃 About Us\nVictory Milestone recruitment agency"
        body = """_*Who we are*_\n\nWe are a leading recruitment agency that aims at providing the best services to companies and job seekers\n\n_*What we do*_\n\n📌Human Resource solutions\n📌Recruitment and Training Services\n📌Job Placement and Salary Negotiations\n📌Insurance Services (Medical, Funeral, Business, All Risk)\n\n*Click on button below to browse*⬇⬇⬇"""
        return Utils.get_menu_action(self, data, message, body)

    def get_contact_us(self, data):
        message = "📃 Contact Us"
        body = """_*Contact Details*_\n\n📞Phone: +263 719156157\n📧Email:info@victorymilestone.co.zw\n🌐Website:www.victorymilestone.co.zw\n📍Address: 92C East Rd, Belgravia, Harare, Zimbabwe\n\n*Click on button below to browse*⬇⬇⬇"""
        return Utils.get_menu_action(self, data, message, body)

    def get_menu_action(self, data, message, body):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": message},
                "body": {"text": body},
                "action": {
                    "button": "Menu Options",
                    "sections": [
                        {
                            "title": "Options",
                            "rows": [
                                {
                                    "id": "5",
                                    "title": "📖About Us",
                                    "description": "View more information about us and our services",
                                },
                                {
                                    "id": "2",
                                    "title": "🔄Update Profile",
                                    "description": "Update your personal information",
                                },
                                {
                                    "id": "3",
                                    "title": "🗒️Browse Vacancies",
                                    "description": "View job listings and/or apply",
                                },
                                {
                                    "id": "1",
                                    "title": "🗂️Upload Documents",
                                    "description": "Upload qualifications or other documents",
                                },
                                {
                                    "id": "4",
                                    "title": "✅View your applications",
                                    "description": "View jobs that your have applied for",
                                },
                                {
                                    "id": "6",
                                    "title": "✉️Contact Us",
                                    "description": "View our contact details",
                                },
                                {
                                    "id": "7",
                                    "title": "💬FAQs",
                                    "description": "Frequently Asked Questions",
                                },
                            ],
                        }
                    ],
                },
            },
        }

    def get_faq(self, data):
        message = "📃 FAQs"
        body = """_*FAQs*_\n\n*1. What are the benefits of registering*\n\nOur agency is highly reputable, customer centric automotive recruitment agency, with an array of expertise at our disposal. We have in-depth market knowledge and fantastic network relations. We also manage your application and will liaise with the client on your behalf. Our agency can also give CV feedback, interview advice and negotiate salaries at offer stage.\n\n*Click on button below to browse*⬇⬇⬇"""
        return Utils.get_menu_action(self, data, message, body)

    def get_document_type_client(self, data, document_types_list):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "🗂️Upload Documents"},
                "body": {"text": "Select the document type below"},
                "action": {
                    "button": "Document Options",
                    "sections": [{"title": "Options", "rows": document_types_list}],
                },
            },
        }

    def get_upload_document(self, data, document_type):
        return Utils.generic_message(
            self,
            data,
            f"📎Upload Document\n\nPlease select the *{document_type}* you would like to upload\n*Document should be in pdf/docx/jpg/jpeg formats*",
        )

    def get_edit_field(self, data):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "🔄Update Profile"},
                "body": {"text": "Select the field to update below"},
                "action": {
                    "button": "Edit Options",
                    "sections": [
                        {
                            "title": "Options",
                            "rows": [
                                {
                                    "id": "1",
                                    "title": "👤First Name",
                                    "description": "Update your first name",
                                },
                                {
                                    "id": "2",
                                    "title": "👤Last Name",
                                    "description": "Update your last name",
                                },
                                {
                                    "id": "3",
                                    "title": "📧Email",
                                    "description": "Update your email address",
                                },
                                {
                                    "id": "4",
                                    "title": "📞Phone Number",
                                    "description": "Update your phone number",
                                },
                                {
                                    "id": "5",
                                    "title": "📅Date of Birth",
                                    "description": "Update your date of birth",
                                },
                                {
                                    "id": "6",
                                    "title": "🏠Address",
                                    "description": "Update your address",
                                },
                                {
                                    "id": "7",
                                    "title": "📇Profile Photo",
                                    "description": "Update your profile photo",
                                },
                                {
                                    "id": "8",
                                    "title": "📇Passport",
                                    "description": "Update your passport",
                                },
                                {
                                    "id": "9",
                                    "title": "👨‍👩‍👧‍👦Gender",
                                    "description": "Update your Gender",
                                },
                            ],
                        }
                    ],
                },
            },
        }

    def get_industries(self, data, industries_list):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "🏢Select Industry"},
                "body": {"text": "Select the industry below"},
                "action": {
                    "button": "Industry Options",
                    "sections": [{"title": "Options", "rows": industries_list}],
                },
            },
        }

    def get_job_list(self, data, job_list):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "🏢Select Vacancy"},
                "body": {"text": "Select the vacancy below"},
                "action": {
                    "button": "Vacancy Options",
                    "sections": [{"title": "Options", "rows": job_list}],
                },
            },
        }

    def get_application_confirmation(self, data, job_title):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": f"📝Application Confirmation\n\nYou are about to apply for the *{job_title}* vacancy. Please confirm your application by clicking on the button below"
                },
                "action": {
                    "buttons": [
                        {
                            "type": "reply",
                            "reply": {
                                "id": "1",
                                "title": "Confirm Application",
                            },
                        },
                        {
                            "type": "reply",
                            "reply": {
                                "id": "2",
                                "title": "Cancel Application",
                            },
                        },
                    ]
                },
            },
        }

    def get_normal_response(self, data, message, body):
        return Utils.get_menu_action(self, data, message, body)

    def get_applications(self, data, applications_list):
        return {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": data["from_phone_number"],
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": "📃Applications"},
                "body": {"text": "Select the application below"},
                "action": {
                    "button": "Application Options",
                    "sections": [{"title": "Options", "rows": applications_list}],
                },
            },
        }

    def get_application_details(self, data, application_details):
        return Utils.generic_message(self, data, application_details)
