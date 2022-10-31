from flask import json, request
# from werkzeug._compat import text_type
from werkzeug.exceptions import HTTPException

from piscis.config.global_config import global_config
from piscis.core.multiplemeta import MultipleMeta


class APIException(HTTPException, metaclass=MultipleMeta):
    code = 500
    message = "抱歉，服务器未知错误"
    error_code = 9999
    headers = {"Content-Type": "application/json"}
    _config = True

    def __init__(self):
        if self._config:
            code_message = global_config.message
            msg = code_message.get(self.error_code)
            if msg:
                self.message = msg
        super(APIException, self).__init__(self.message, None)

    def __init__(self, error_code: int):
        self.error_code = error_code
        if self._config:
            code_message = global_config.message
            msg = code_message.get(self.error_code)
            if msg:
                self.message = msg
        super(APIException, self).__init__(self.message, None)

    def __init__(self, message: str):
        self.message = message
        super(APIException, self).__init__(self.message, None)

    def __init__(self, error_code: int, message: str):
        self.error_code = error_code
        self.message = message
        super(APIException, self).__init__(self.message, None)

    def __init__(self, message: dict):
        self.message = message
        super(APIException, self).__init__(self.message, None)

    def __init__(self, error_code: int, message: dict):
        self.error_code = error_code
        self.message = message
        super(APIException, self).__init__(self.message, None)

    def set_code(self, code: int):
        self.code = code
        return self

    def set_error_code(self, error_code: int):
        self.error_code = error_code
        return self

    def add_headers(self, headers: dict):
        headers_merged = headers.copy()
        headers_merged.update(self.headers)
        self.headers = headers_merged
        return self

    def get_body(self, environ=None, scope=None):
        body = dict(
            message=self.message,
            error_code=self.error_code,
            # request=request.method + "  " + self.get_url_no_param(),
        )
        text = json.dumps(body)
        # return text_type(text)
        return text

    @staticmethod
    def get_url_no_param():
        full_path = str(request.full_path)
        main_path = full_path.split("?")
        return main_path[0]

    def get_headers(self, environ=None, scope=None):
        return [(k, v) for k, v in self.headers.items()]


class Success(APIException):
    code = 200
    message = "OK"
    error_code = 0


class Failed(APIException):
    code = 400
    message = "Failed"
    error_code = 10200


class UnAuthorization(APIException):
    code = 401
    message = "Authorization Failed"
    error_code = 10000


class UnAuthentication(APIException):
    code = 401
    message = "Authentication Failed"
    error_code = 10010


class NotFound(APIException):
    code = 404
    message = "Not Found"
    error_code = 10021


class ParameterError(APIException):
    code = 400
    message = "Parameters Error"
    error_code = 10030


class DocParameterError(APIException):
    code = 400
    message = {"parameter": ["validation error info", ]}
    error_code = 10030
    _config = False


class TokenInvalid(APIException):
    code = 401
    message = "Token Invalid"
    error_code = 10040


class TokenExpired(APIException):
    code = 422
    message = "Token Expired"
    error_code = 10052


class InternalServerError(APIException):
    code = 500
    message = "Internal Server Error"
    error_code = 9999


class Duplicated(APIException):
    code = 400
    message = "Duplicated"
    error_code = 10060


class Forbidden(APIException):
    code = 401
    message = "Forbidden"
    error_code = 10070


class FileTooLarge(APIException):
    code = 413
    message = "File Too Large"
    error_code = 10110


class FileTooMany(APIException):
    code = 413
    message = "File Too Many"
    error_code = 10120


class FileExtensionError(APIException):
    code = 401
    message = "FIle Extension Not Allowed"
    error_code = 10130


class MethodNotAllowed(APIException):
    code = 401
    message = "Method Not Allowed"
    error_code = 10080


class RequestLimit(APIException):
    code = 401
    message = "Too Many Requests"
    error_code = 10140


class PageUnAuthorization(APIException):
    code = 401
    message = "Page UnAuthorization Failed"
    error_code = 10150


class ButtonUnAuthorization(APIException):
    code = 401
    message = "Button UnAuthorization Failed"
    error_code = 10151
