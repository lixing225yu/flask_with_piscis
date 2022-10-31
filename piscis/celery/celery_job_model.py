from piscis.db.database import InfoCrud
from sqlalchemy import Column, Integer, String, Text, DateTime

__all__ = ['CeleryJob']


class CeleryJob(InfoCrud):
    __tablename__ = 'celery_job'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(64), nullable=False, comment="task id")
    module_name = Column(String(128), comment="模块名")
    func_name = Column(String(64), comment="方法名")
    args = Column(String(512), comment="参数")
    kwargs = Column(String(512), comment="字典参数")
    queue_name = Column(String(32), comment="队列名")
    pre_publish_at = Column(DateTime(timezone=True))
    post_publish_at = Column(DateTime(timezone=True))
    pre_run_at = Column(DateTime(timezone=True))
    post_run_at = Column(DateTime(timezone=True))
    status = Column(String(16), comment="状态")
    task_type = Column(String(16), comment="task 类型")
    result = Column(String(512), comment="执行结果")
    exception = Column(String(512), comment="异常信息")
