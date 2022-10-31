from pydantic import BaseModel, validator
from pydantic import Field


class PagedSchema(BaseModel):
    page: int = Field(default=1, description="页码", gt=0)
    page_size: int = Field(default=20, description="每页数量", gt=0, le=50)


class PasswordRequiredSchema(BaseModel):
    password: str = Field(description="账号密码")

    @validator("password", always=True)
    def v_check_password(cls, value):
        if value != '123':
            raise ValueError("密码不正确")
        return value


class QueryByIdSchema(BaseModel):
    id: int = Field(description='id')

