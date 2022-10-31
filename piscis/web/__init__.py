from flask import Flask, current_app
from flask_siwadoc import SiwaDoc
from werkzeug.local import LocalProxy

from .manager import Manager
from .response import JSONEncoder, auto_response
from piscis.exception import APIException, InternalServerError
from werkzeug.exceptions import HTTPException
from piscis.db.database import db
from piscis.config.global_config import global_config
from ..logger.syslogger import SysLogger


class Piscis(object):
    def __init__(
            self,
            app: Flask = None,  # flask app
            user_model = None,
            siwa = None,
            jsonencoder = None,  # 序列化器
            enable_handle = True,  # 是否启用全局异常处理
            syslogger=True,  # 是否使用自定义系统运行日志
            **kwargs,  # 保留配置项
    ):
        self.set_global_config(**kwargs)
        self.app = app
        self.manager = None
        if app is not None:
            self.init_app(
                app,
                user_model,
                siwa,
                jsonencoder,
                enable_handle,
                syslogger,
            )

    def init_app(
            self,
            app,
            user_model,
            siwa = None,
            jsonencoder=None,
            enable_handle=True,
            syslogger=True,
    ):
        self.jsonencoder = jsonencoder
        self.enable_auto_jsonify(app)
        siwa.init_app(app)
        db.init_app(app)
        self.app = app
        self.manager = Manager(user_model)
        self.app.extensions['manager'] = self.manager
        enable_handle and self.handle_error(app)
        syslogger and SysLogger(app)

    def set_global_config(self, **kwargs):
        for k, v in kwargs.items():
            if k.startswith("config_"):
                global_config[k[7:]] = v

    def handle_error(self, app):
        @app.errorhandler(Exception)
        def handler(e):
            if isinstance(e, APIException):
                return e
            if isinstance(e, HTTPException):
                code = e.code
                message = e.description
                error_code = 20000
                return APIException(error_code, message).set_code(code)
            else:
                if not app.config["DEBUG"]:
                    import traceback

                    app.logger.error(traceback.format_exc())
                    return InternalServerError()
                else:
                    raise e

    def enable_auto_jsonify(self, app):
        app.json_encoder = self.jsonencoder or JSONEncoder
        app.make_response = auto_response(app.make_response)
