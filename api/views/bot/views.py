from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from services.helpers.whatsapp import is_valid_message, format_message


class WebhookView(APIView):
    parser_classes = (JSONParser,)

    # This webhook is for whatsapp cloud api
    def post(self, request):
        try:
            print("INCOMING DATA:", request.data)
            valid = is_valid_message(request.data)
            if valid:
                success, response, user_status, user = format_message(request.data)
                if success:
                    print("Formatted Data", response, user_status)
                    service = WhatsappService(response, user_status, user=user)
                    service.process()
                    return JsonResponse(
                        {"message": "received"}, status=status.HTTP_200_OK
                    )
                pass
            else:
                print("INVALID MESSAGE")
        except Exception as e:
            print("Failed to action => error", e)
        return JsonResponse({"message": "received"}, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        form_data = request.query_params
        mode = form_data.get("hub.mode")
        token = form_data.get("hub.verify_token")
        challenge = form_data.get("hub.challenge")
        print(mode, token, challenge)
        return HTTPResponse(challenge, 200)
