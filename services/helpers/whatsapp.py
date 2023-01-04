from users.models import User


def is_valid_message(incoming_whatsapp_message: dict) -> bool:
    """
    Check if a message is valid
    """
    if incoming_whatsapp_message["entry"][0]["changes"][0]["value"].get("messages"):
        return True
    return False


def format_message(incoming_message):
    # common fields across all messages
    try:
        formatted_message = {
            "to_phone_number": incoming_message.get("to"),
            "from_phone_number": incoming_message["entry"][0]["changes"][0]["value"][
                "messages"
            ][0]["from"],
            "message_id": incoming_message["entry"][0]["changes"][0]["value"][
                "messages"
            ][0]["id"],
            "whatsapp_name": incoming_message["entry"][0]["changes"][0]["value"][
                "contacts"
            ][0]["profile"]["name"],
            "message_type": incoming_message["entry"][0]["changes"][0]["value"][
                "messages"
            ][0]["type"],
        }
        # extract data based on type of message
        if formatted_message["message_type"] == "text":
            formatted_message["message"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["text"]["body"]

        if formatted_message["message_type"] == "button":
            formatted_message["message"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["button"]["text"]

        if formatted_message["message_type"] == "interactive":
            formatted_message["interactive_type"] = incoming_message["entry"][0][
                "changes"
            ][0]["value"]["messages"][0]["interactive"]["type"]
            if formatted_message["interactive_type"] == "button_reply":
                formatted_message["button_reply"] = incoming_message["entry"][0][
                    "changes"
                ][0]["value"]["messages"][0]["interactive"]["button_reply"]

            if formatted_message["interactive_type"] == "list_reply":
                formatted_message["list_reply"] = incoming_message["entry"][0][
                    "changes"
                ][0]["value"]["messages"][0]["interactive"]["list_reply"]

        if formatted_message["message_type"] == "document":
            formatted_message["document"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["document"]
            formatted_message["media_id"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["document"]["id"]

        if formatted_message["message_type"] == "image":
            formatted_message["image"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["image"]
            formatted_message["media_id"] = incoming_message["entry"][0]["changes"][0][
                "value"
            ]["messages"][0]["image"]["id"]

        user = User.objects.filter(
            phone_number=formatted_message["from_phone_number"]
        ).first()
        if user:
            return True, formatted_message, True, user
        else:
            return True, formatted_message, False, None
    except Exception as e:
        print("** The incoming message is malformed or a status message", e)
        return False, "Malformed message", False, None
