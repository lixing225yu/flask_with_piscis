import pickle
import numbers
from flask import current_app
import datetime


class BaseCache(object):
    def set(self, key, value, timeout):
        raise Exception('method not implemented')

    def set_object(self, key, value, timeout):
        self.set(key, pickle.dumps(value), timeout)

    def get(self, key):
        raise Exception('method not implemented')

    def get_object(self, key):
        v = self.get(key)
        if v:
            return pickle.loads(v)
        return v

    def delete(self, key_or_keys):
        raise Exception('method not implemented')

    def clear(self, pattern):
        raise Exception('method not implemented')

    @classmethod
    def _check_value(cls, v):
        if v is None:
            return True
        elif isinstance(v, list):
            for vv in v:
                if not cls._check_value(vv):
                    return False
        elif isinstance(v, dict):
            for kk, vv in v.items():
                if not cls._check_value(vv):
                    return False
        elif not isinstance(v, (str, numbers.Number, bool, datetime.date)):
            return False

        return True
