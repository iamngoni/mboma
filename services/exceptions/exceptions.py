#
#  exceptions.py
#  mboma
#
#  Created by Ngonidzashe Mangudya on 12/2/2023.


class APIException(Exception):
    def __init__(self, message=None, status_code=500):
        self.status_code = status_code
        self.message = message if message else "Service Error"

    def get_status_code(self):
        return self.status_code

    def to_dict(self):
        return {"status_code": self.status_code, "message": self.message}


class ValidationException(APIException):
    def __init__(self, message=None):
        self.status_code = 400
        self.message = message if message else "Invalid value"


class MalformedWhatsappMessageError(APIException):
    def __init__(self, message=None):
        self.status_code = 400
        self.message = message if message else "Unexpected message format"


class ItemNotFoundException(APIException):
    def __init__(self, message=None):
        self.status_code = 404
        self.message = message if message else "Item not found"


class TransitionError(APIException):
    def __init__(self, message=None):
        self.message = message if message else "Failed state transition"


class CompressionError(APIException):
    def __init__(self, message=None):
        self.message = message if message else "Failed to compress"


class WhatsappAPIException(APIException):
    def __init__(self, message=None):
        self.message = message if message else "Sending Whatsapp message failed"
