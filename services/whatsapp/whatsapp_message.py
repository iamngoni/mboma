from decouple import config
import json
import requests
from django.conf import settings
from loguru import logger

from services.helpers.api_response import api_response


class WhatsappMessage:
    def __init__(self, payload: dict):
        self.payload = payload

    def send(self):
        headers = {
            "Authorization": f'Bearer {config("WHATSAPP_TOKEN")}',
            "Content-Type": "application/json",
        }

        payload = json.dumps(self.payload)

        logger.info(f"send payload back to whatsapp -> {payload}")

        # check if message is an image and cache
        if self.payload.get("type") == "image":
            headers["Cache-Control"] = "max-age=604800"

        response = requests.request(
            "POST",
            f"{config('WHATSAPP_URL')}/{config('WHATSAPP_ID')}/messages",
            headers=headers,
            data=payload,
        )

        # if successful take message id and return it
        # {"messaging_product":"whatsapp","contacts":[{"input":"263777213388","wa_id":"263777213388"}],"messages":[{"id":"wamid.HBgMMjYzNzc3MjEzMzg4FQIAERgSRTYwREI2Q0YzOEQyMzNDMzVBAA=="}]}

        logger.info("---------------------------------------")
        logger.info(f"WhatsApp Response: {response.status_code}")
        logger.info("---------------------------------------")
        logger.info(response.json())
        logger.info("---------------------------------------")
        response_data = response.json()
        if response.status_code == 200:
            return response_data["messages"][0]["id"]
        else:
            return None
