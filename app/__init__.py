import sys

from traceback import format_exception

from flask import Flask
from flask_siwadoc import SiwaDoc

from piscis.exception import APIException
from piscis.web import InternalServerError
from piscis.web import Piscis

from config import global_config, stage

siwa = SiwaDoc()


def load_app_config(app):
    """
    根据指定配置环境自动加载对应环境变量和配置类到app config
    """
    # 读取配置类
    app.config.from_mapping()
    app.config.from_object(f"config.flaskconfig.{stage.capitalize()}Config")


def create_app(register_all=True, **kwargs):
    app = Flask(__name__)
    load_app_config(app)

    if register_all:
        Piscis(app, siwa=siwa, **kwargs)
        register_blueprints(app)

    @app.errorhandler(Exception)
    def error_500(error):
        if isinstance(error, APIException):
            return error
        e_type, value, tb = sys.exc_info()
        app.logger.info("".join(format_exception(e_type, value, tb)))
        return InternalServerError(str(error))

    return app


def register_blueprints(app):
    from app.controllers.views.demo_view import bp as demo_bp
    def deco_url_prefix(prefix, module_name):
        prefix = f"{app.config.get('API_PREFIX') or '/api'}{prefix}"
        global_config.module.setdefault(prefix, module_name)
        return prefix

    app.register_blueprint(demo_bp, url_prefix=deco_url_prefix("/demo", "demo"))
