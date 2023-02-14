#
#  views.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.

from loguru import logger
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from services.dtos.whatsapp_message import WhatsAppMessageDTO
from services.helpers.api_response import api_response
from services.helpers.whatsapp_helpers import WhatsAppHelpers
from services.whatsapp.whatsapp_service import WhatsAppService
from django.shortcuts import HttpResponse


class WhatsAppView(APIView):
    parser_classes = (JSONParser,)

    # This webhook is for whatsapp cloud api
    def post(self, request):
        try:
            requires_system_action = WhatsAppHelpers.requires_system_action(
                request.data
            )
            if requires_system_action:
                message: WhatsAppMessageDTO = WhatsAppHelpers.format_message(
                    request.data
                )
                service = WhatsAppService(message)
                service.process()
            else:
                logger.info("Not an incoming message. Probably an event notification")
        except Exception as exc:
            logger.info(f"Failed to action -> {exc}")

        return api_response(request, data={"message": "received"})

    def get(self, request, *args, **kwargs):
        """Verify messages from Whatsapp
        https://developers.facebook.com/docs/graph-api/webhooks/getting-started
        """
        try:
            form_data = request.query_params
            mode = form_data.get("hub.mode")
            token = form_data.get("hub.verify_token")
            challenge = form_data.get("hub.challenge")
            logger.info(f"mode: {mode}, token: {token}, challenge: {challenge}")

            return HttpResponse(challenge, 200)
        except Exception as e:
            logger.error(f"Error: {e}")
            return HttpResponse("Error", 500)


class PaynowView(APIView):
    parser_classes = (JSONParser,)

    def post(self, request):
        pass
