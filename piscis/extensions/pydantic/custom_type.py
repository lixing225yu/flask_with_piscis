from datetime import datetime
from typing import List, TypeVar, Generic
from pydantic.utils import update_not_none

__all__ = ['choice', "date_field"]

T = TypeVar('T')


class Choice(Generic[T]):
    values: List[T]

    def __init__(self, values):
        self.values = values

    @classmethod
    def __modify_schema__(cls, field_schema) -> None:
        update_not_none(field_schema, values=cls.values)

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: T) -> T:
        t = type(cls.values[0])
        if t(value) not in cls.values:
            raise ValueError("值范围不合法")
        return t(value)


def choice(values: List):
    return type("Choice", (Choice, type(values[0])), dict(values=values))


class DateField(str):
    formats: List[str]

    def __init__(self, formats: List[str]):
        self.formats = formats

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value: str) -> str:
        if value:
            success = False
            for fmt in cls.formats:
                try:
                    datetime.strptime(value, fmt)
                    success = True
                    break
                except:
                    pass
            if not success:
                raise ValueError("日期类型不正确")
        return value


def date_field(*formats):
    if not formats:
        formats = ['%Y-%m-%d']
    return type("DateField", (DateField,), dict(formats=formats))
