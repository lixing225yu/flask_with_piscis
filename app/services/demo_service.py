from app.controllers.schemas.demo_schema import UserListQuerySchema
from app.services import gen_paged_data
from random import randint, choice

from const.enums.basic import UserTypeEnum


class DemoService:
    @classmethod
    def get_user_list(cls, params: UserListQuerySchema):
        total = 50
        items = []
        for i in range(total):
            items.append({'name': f'{params.name}_i' if params.name else f'user_{i}',
                          'user_type': choice(UserTypeEnum.value_list())})
        if params.user_type:
            items = [i for i in items if i['user_type'] == params.user_type]
            total = len(items)
        paged_items = items[(params.page - 1) * params.page_size:params.page + 1 * params.page_size]
        return gen_paged_data(params.page, params.page_size, total, paged_items)
