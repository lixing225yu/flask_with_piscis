from collections import namedtuple
from enum import Enum
from types import DynamicClassAttribute

T = namedtuple("Field", ["value", "desc"])


class FieldEnum(Enum):
    @DynamicClassAttribute
    def value(self):
        """直接获取namedtuple的value的值"""
        return self._value_.value

    @DynamicClassAttribute
    def desc(self):
        """直接获取namedtuple的desc的值"""
        return self._value_.desc

    @classmethod
    def by(cls, value, default=None):
        """根据value获取对应的枚举"""
        for field, enum in cls._value2member_map_.items():
            if value == field.value:
                return enum
        if default:
            return default
        else:
            raise ValueError(f"{cls.__name__}(value={value}):没有对应的枚举")

    @classmethod
    def by_desc(cls, text, default=None):
        """根据desc获取对应的枚举"""
        for field, enum in cls._value2member_map_.items():
            if text == field.desc:
                return enum
        if default:
            return default
        else:
            raise ValueError(f"{cls.__name__}(desc={text}):没有对应的枚举")

    @DynamicClassAttribute
    def field(self):
        """返回一个namedtuple"""
        return self._value_

    @classmethod
    def iter(cls):
        """返回一个迭代器对象，方便遍历"""
        for value in cls._value2member_map_.values():
            yield value

    @classmethod
    def to_list(cls, t_field="text", v_field="value"):
        return [{t_field: f.desc, v_field: f.value} for f in cls]

    @classmethod
    def value_list(cls):
        return [f.value for f in cls]


class Gender(FieldEnum):
    """一个例子"""

    MAN = T(1, "男")
    WOMAN = T(2, "女")
    NULL = T(0, "未知")


if __name__ == "__main__":

    print(Gender.MAN.value)
    print(Gender.MAN.desc)
    print(Gender.by_desc("男"))
    print(Gender.by(2).desc)
    for f in Gender:
        print(f.name)
    print(Gender.to_list())
    print(Gender.to_list(t_field="key", v_field="value"))
    print(Gender.value_list())
