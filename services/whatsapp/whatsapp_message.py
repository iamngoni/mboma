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
        logger.info(f"response from whatsapp -> {response.text}")
