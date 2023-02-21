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
from api.views.bot.tasks import send_order_confirmation_text

from shop.models import Order


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

    def post(self, request, *args, **kwargs):
        """
        Get the following fields from the paynow request params and update order using reference:
        reference, amount, paynowreference, pollurl, status['Paid', 'Created', 'Sent', 'Cancelled', 'Disputed', 'Refunded'], hash
        """
        # get request query params
        data = request.query_params
        reference = data.get("reference")
        paynow_reference = data.get("paynowreference")
        poll_url = data.get("pollurl")
        status = data.get("status")
        hash = data.get("hash")

        order = Order.get_item_by_id(reference)

        if order:
            order.paynow_reference = paynow_reference
            order.poll_url = poll_url
            order.status = status
            order.hash = hash

            if status == "Paid":
                order.paid = True

            order.save()

            if order.paid:
                # send order confirmation
                send_order_confirmation_text.delay(order)
        else:
            logger.info("Order not found")

        return api_response(request)
