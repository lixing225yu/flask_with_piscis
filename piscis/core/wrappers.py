import functools


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton


@Singleton
class IdPrefixManager:
    def __init__(self):
        self.class_prefix_map = {}

    def register(self, prefix: str = ''):
        def deco(cls):
            self.storage(cls, prefix)
            return cls

        return deco

    def storage(self, cls: type, _prefix: str):
        self.class_prefix_map.setdefault(cls.__name__, _prefix)

    def get_prefix(self, cls: type) -> str:
        return self.class_prefix_map.get(cls.__name__)


id_prefix_manager = IdPrefixManager()
