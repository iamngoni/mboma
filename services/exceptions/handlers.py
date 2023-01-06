from rest_framework.views import exception_handler

from services.helpers.api_response import api_response


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data["status_code"] = response.status_code

    # create custom fake request object
    request = FakeRequestClass(
        method=context.get("request").method,
        headers=str(context.get("request").headers),
        path=context.get("request").path,
    )

    return api_response(
        request=request,
        message=response.data.get("detail") if response else exc,
        num_status=response.data.get("status_code") if response else 500,
        bool_status=False,
        issues=str(exc),
    )


class FakeRequestClass:
    def __init__(self, method, headers, path):
        self.method = method
        self.headers = headers
        self.path = path
