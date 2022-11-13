import os

from config import settings

# base
# daemon = True
from multiprocessing import cpu_count

bind = f"0.0.0.0:{settings.port}"  # 绑定ip和端口号
backlog = 512  # 监听队列, 等待服务的客户的数量
chdir = os.path.dirname(os.path.abspath(__file__))  # gunicorn要切换到的目的工作目录

# network
timeout = 30  # 超时
keepalive = 60  # 服务器保持连接的时间，能够避免频繁的三次握手过程
graceful_timeout = 30  # 重启时限
forwarded_allow_ips = "*"  # 允许哪些ip地址来访问

# process
worker_class = "gevent"  # 默认的是sync模式
workers = cpu_count() * 2  # 进程数
pidfile = os.path.join(chdir, f"{settings.project_name}.pid")  # 保存gunicorn的进程pid的文件

# log
capture_output = True  # 是否捕获输出
loglevel = "debug"  # 日志级别，这个日志级别指的是错误日志的级别，而访问日志的级别无法设置
access_log_format = "%(p)s %(t)s %(r)s %(s)s %(T)s"
accesslog = os.path.join(chdir, settings.log_dir, f"{settings.project_name}_guc_acc.log")  # 访问日志文件
errorlog = os.path.join(chdir, settings.log_dir,  f"{settings.project_name}_guc_err.log")  # 错误日志文件
