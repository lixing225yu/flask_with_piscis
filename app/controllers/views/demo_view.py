from flask import Blueprint
from app import siwa
from app.controllers.schemas.demo_schema import UserListQuerySchema
from app.services.demo_service import DemoService
from piscis.extensions.pydantic.core import validate


bp = Blueprint("demo", __name__)


@bp.route('/user-list')
@validate()
@siwa.doc(query=UserListQuerySchema, description="", summary='分页获取用户信息', tags=['demo'])
def user_list(query: UserListQuerySchema):
    result = DemoService.get_user_list(query)
    return result
