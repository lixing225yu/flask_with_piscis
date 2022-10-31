from typing import List, TypeVar, Generic, Type
from pydantic.utils import update_not_none

__all__ = ['choice']

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


def choice(values: List[int]):
    return type("ChoiceInt", (Choice, int), dict(values=values))


def choice_str(values: List[str]):
    return type("ChoiceStr", (Choice, str), dict(values=values))
