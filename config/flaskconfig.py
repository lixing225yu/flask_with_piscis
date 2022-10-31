from piscis.config.global_config import global_config


class BaseConfig(object):
    """
    基础配置
    """

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 动态追踪修改设置
    SQLALCHEMY_ECHO = False  # 查询时会显示原始SQL语句
    SQLALCHEMY_POOL_SIZE = 16  # 连接池大小
    SQLALCHEMY_POOL_TIMEOUT = 10  # 池中没有线程最多等待的时间，否则报错
    SQLALCHEMY_POOL_RECYCLE = 1200  # 多久之后对线程池中的线程进行一次连接的回收（重置）
    LOG = {
        "LEVEL": "DEBUG",
        "DIR": "logs",
        "SIZE_LIMIT": 1024 * 1024 * 5,
        "REQUEST_LOG": True,
        "FILE": True,
    }


class DevelopmentConfig(BaseConfig):
    """
    开发环境配置
    """

    SQLALCHEMY_DATABASE_URI = ""  # 默认连接串


class ProductionConfig(BaseConfig):
    """
    生产环境配置
    """

    ""
    SQLALCHEMY_DATABASE_URI = ""  # 默认连接串
