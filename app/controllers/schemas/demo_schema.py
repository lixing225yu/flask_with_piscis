from typing import Optional

from pydantic import Field

from app.controllers.schemas.common_schema import PagedSchema
from const.enums.basic import UserTypeEnum
from piscis.extensions.pydantic.custom_type import choice


class UserListQuerySchema(PagedSchema):
    name: Optional[str] = Field(description='用户名称')
    user_type: Optional[choice(UserTypeEnum.value_list())] = Field(description="用户类型")
