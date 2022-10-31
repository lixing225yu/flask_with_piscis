__all__ = ["Manager", "manager"]

from flask import current_app
from werkzeug.local import LocalProxy


class Manager(object):
    """ manager for piscis """

    def __init__(self, user_model=None):
        self.user_model = user_model

    def find_user(self, **kwargs):
        return self.user_model.query.filter_by(**kwargs).first()

    def verify_user(self, username, password):
        return self.user_model.verify(username, password)


def get_manager():
    _manager = current_app.extensions['manager']
    if _manager:
        return _manager
    else:
        app = current_app._get_current_object()
        with app.app_context():
            return app.extensions['manager']


# 获得manager实例
# 注意，仅仅在flask的上下文栈中才可获得
manager: Manager = LocalProxy(lambda: get_manager())