from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import simplejson as json
from flask import jsonify
from flask.json import JSONEncoder as _JSONEncoder
from pydantic import BaseModel


class CommonResult(object):
    error_code = 0
    message = ''
    data = None

    def __init__(self, error_code=0, message='', data=None):
        if error_code is not None:
            self.error_code = error_code
        if message is not None:
            self.message = message
        if data is not None:
            self.data = data


class JSONEncoder(_JSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.dict()
        if isinstance(o, (int, list, set, tuple)):
            return json.dumps(o, cls=JSONEncoder)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.strftime("%Y-%m-%d")
        if isinstance(o, Enum):
            return o.value
        if isinstance(o, Decimal):
            return json.dumps(o, use_decimal=True)
        if hasattr(o, "keys") and hasattr(o, "__getitem__"):
            return dict(o)
        return JSONEncoder.default(self, o)


def auto_response(func):
    def make_a_response(o):
        if isinstance(o, CommonResult):
            o = jsonify(error_code=o.error_code, message=o.message, data=o.data)
        elif isinstance(o, BaseModel):
            o = jsonify(error_code=0, message='', data=o.dict())
        elif (
                (hasattr(o, "keys") and hasattr(o, "__getitem__"))
                or isinstance(o, (int, tuple, list, set, complex, Decimal, Enum))
        ):
            o = jsonify(error_code=0, message='', data=o)
        return func(o)

    return make_a_response
