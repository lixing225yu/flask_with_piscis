import os

from config import global_config

# base
# daemon = True

bind = "0.0.0.0:8888"  # 绑定ip和端口号
backlog = 512  # 监听队列, 等待服务的客户的数量
chdir = os.path.dirname(os.path.abspath(__file__))  # gunicorn要切换到的目的工作目录

# network
timeout = 30  # 超时
keepalive = 60  # 服务器保持连接的时间，能够避免频繁的三次握手过程
graceful_timeout = 30  # 重启时限
forwarded_allow_ips = "*"  # 允许哪些ip地址来访问

# process
worker_class = "gevent"  # 默认的是sync模式
# workers = 4  # 进程数
workers = 1  # 进程数
threads = 1  # 指定每个进程开启的线程数
pidfile = os.path.join(chdir, "piscis.pid")  # 保存gunicorn的进程pid的文件

# log
capture_output = True  # 是否捕获输出
loglevel = "debug"  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = "%(p)s %(t)s %(r)s %(s)s %(T)s"
accesslog = os.path.join(chdir, global_config.settings.log_dir, "access.log")  # 访问日志文件
errorlog = os.path.join(chdir, global_config.settings.log_dir, "error.log")  # 错误日志文件
