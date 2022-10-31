import datetime
from functools import wraps

from flask import Response, request, g
from sqlalchemy import Column, Integer, String, Text
from piscis.db.database import InfoCrud, db
import sqlalchemy
from jinja2 import Template
from piscis.config.global_config import global_config
from piscis.core.wrappers import id_prefix_manager
from piscis.exception import Failed


@id_prefix_manager.register("")
class Log(InfoCrud):
    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    id = Column(String(32), primary_key=True)
    org_id = Column(String(32), comment="租户id")
    user_id = Column(String(32), nullable=False, comment="用户id")
    message = Column(Text, comment="日志信息")
    error_code = Column(Integer(), comment="response错误码")
    method = Column(String(16), comment="请求方法")
    path = Column(String(64), comment="请求路径")
    module = Column(String(32), comment='模块名称')

    def dynamic_id_prefix(self):
        return self.__tablename__[-6:]

    table_prefix = 'app_log'


class DbLogger(object):
    """
    用户行为日志记录器
    """
    template = None

    def __init__(self, template=None):
        if template:
            self.template: str = template
        elif self.template is None:
            raise Failed("日志模板不能为空")
        self.message = ""
        self.response = None
        self.user = None

    def __call__(self, func):
        @wraps(func)
        def wrap(*args, **kwargs):
            response: Response = func(*args, **kwargs)
            self.response = response
            self.user = g.get('current_user')
            # if not self.user:
            #     raise Exception("Logger must be used in the login state")
            self.message = self._parse_template()
            self.write_log()
            return response

        return wrap

    def write_log(self):
        user_id = 0
        if self.user and hasattr(self.user, 'is_authenticated') and self.user.is_authenticated:
            user_id = self.user.id
        # if user_id == 0:
        #     return
        org_id = 0
        if hasattr(self.user, 'org_id'):
            org_id = self.user.org_id
        error_code = getattr(self.response, "error_code", 0)
        month = datetime.datetime.now().strftime('%Y%m')
        session = db.get_session('log')
        model = Log.get_model(month)
        table_name = f'{model.table_prefix}_{month}'
        if not sqlalchemy.inspect(session.bind.engine).has_table(table_name):
            return
        path = request.path
        module = ''
        if global_config.module:
            for k, v in global_config.module.items():
                if path.startswith(k):
                    module = v
                    break
        model.create(
            session=session,
            message=self.message,
            user_id=user_id,
            org_id=org_id,
            error_code=error_code,
            method=request.method,
            path=path,
            module=module,
            commit=True,
        )

    # 解析自定义模板
    def _parse_template(self):
        tpl = Template(self.template)
        message = tpl.render(user=self.user, response=self.response, request=request)
        return message
