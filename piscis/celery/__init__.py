from piscis.config.global_config import global_config
from celery import Celery, signals as celery_signals
from piscis.core import signals
from .celery_job_model import CeleryJob
from piscis.utils.timeutil import now
import json
from flask import Flask
from piscis.db.database import db


class FlaskCelery:
    app: Celery = None
    flask_app: Flask = None

    def __init__(self, flask_config: str = None, **kwargs):
        if not settings.celery:
            return
        conf = settings.celery
        app = Celery(
            settings.project_name,
            broker=conf.broker_url,
        )
        FlaskCelery.app = app
        app.conf.update(conf)

        if flask_config is not None:
            flask_app = Flask(__name__)
            flask_app.config.from_object(flask_config)
            db.init_app(flask_app)
            FlaskCelery.flask_app = flask_app


# @signals.blueprint_loaded.connect
# def _load_tasks(flask_app):
#     if MyCelery.app is None:
#         return
#
#     tasks_packages = [
#         settings.project_name,
#     ]
#
#     if settings.celery.task_packages:
#         tasks_packages.extend(settings.celery.task_packages)
#
#     MyCelery.app.autodiscover_tasks(lambda: tasks_packages)


if celery_signals is not None:
    @celery_signals.before_task_publish.connect
    def before_task_publish_handler(headers=None, declare=None, **others):
        """
        任务发布前回调处理器
        """
        task_id = headers['id']
        task_name = headers['task']
        args = headers['argsrepr']
        kwargs = headers['kwargsrepr']

        queue_name = declare[0].name
        task_type = 'async'  # 异步
        if queue_name.find('schedule') >= 0:
            task_type = 'periodic'  # 定时
        last_dot_index = task_name.rfind('.')
        module_name = task_name[0: last_dot_index]
        func_name = task_name[last_dot_index + 1:]
        if FlaskCelery.flask_app:
            with FlaskCelery.flask_app.app_context():
                session = db.get_session('log')
                CeleryJob.create(session=session,
                                 task_id=task_id,
                                 module_name=module_name,
                                 func_name=func_name,
                                 args=args,
                                 kwargs=kwargs,
                                 queue_name=queue_name,
                                 pre_publish_at=now(),
                                 task_type=task_type,
                                 commit=True
                                 )


    @celery_signals.after_task_publish.connect
    def after_task_publish_handler(headers=None, **other):
        """
        任务发布后回调处理器
        """
        task_id = headers['id']
        if FlaskCelery.flask_app:
            with FlaskCelery.flask_app.app_context():
                session = db.get_session('log')
                job = CeleryJob.get(session=session, task_id=task_id)
                if job:
                    job.update(session=session, post_publish_at=now(), status='post_publish', commit=True)


    @celery_signals.task_prerun.connect
    def task_pre_run_handler(task_id=None, **other):
        """
        任务在worker端开始执行前回调，在worker进程中执行该回调
        """
        if FlaskCelery.flask_app:
            with FlaskCelery.flask_app.app_context():
                session = db.get_session('log')
                job = CeleryJob.get(session=session, task_id=task_id)
                if job:
                    job.update(session=session, pre_run_at=now(), status='pre_run', commit=True)


    @celery_signals.task_postrun.connect
    def task_post_run_handler(task_id=None, state=None, retval=None, **other):
        """
        任务在worker端执行完后回调，在worker进程中执行该回调
        """
        if FlaskCelery.flask_app:
            with FlaskCelery.flask_app.app_context():
                session = db.get_session('log')
                job = CeleryJob.get(session=session, task_id=task_id)
                if job:
                    status = 'success' if state == 'SUCCESS' else 'failure'
                    if retval is None:
                        retval = ''
                    result = json.dumps(retval, ensure_ascii=False)
                    job.update(session=session, post_run_at=now(), status=status, result=result, commit=True)


    @celery_signals.task_failure.connect
    def task_failure_handler(task_id=None, exception=None, **other):
        """
        任务在worker端执行中出现异常后回调，在worker进程中执行该回调
        """
        if FlaskCelery.flask_app:
            with FlaskCelery.flask_app.app_context():
                session = db.get_session('log')
                job = CeleryJob.get(session=session, task_id=task_id)
                if job:
                    job.update(session=session, post_run_at=now(), status='failure', exception=str(exception),
                               commit=True)
