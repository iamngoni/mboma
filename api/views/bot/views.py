from loguru import logger
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from services.helpers.api_response import api_response
from services.helpers.whatsapp import is_valid_message, format_message
from services.whatsapp.whatsapp_service import WhatsappService
from django.shortcuts import HttpResponse


class WebhookView(APIView):
    parser_classes = (JSONParser,)

    # This webhook is for whatsapp cloud api
    def post(self, request):
        try:
            logger.info(f"INCOMING DATA: {request.data}")
            valid = is_valid_message(request.data)
            if valid:
                success, response, user_status, user = format_message(request.data)
                if success:
                    logger.info(f"Formatted Data: {response, user_status}")
                    service = WhatsappService(
                        formatted_message=response, is_registered=user_status, user=user
                    )
                    service.process()
                    return api_response(request, data={"message": "received"})
                pass
            else:
                logger.info("Not an incoming message. Probably an event notification")
        except Exception as exc:
            logger.info(f"Failed to action -> {exc}")

        return api_response(request, data={"message": "received"})

    def get(self, request, *args, **kwargs):
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
