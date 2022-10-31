from sqlalchemy import func, inspect, orm
from sqlalchemy import Column, DateTime
from sqlalchemy.orm.attributes import InstrumentedAttribute
from piscis.core.wrappers import id_prefix_manager
from flask import current_app
from piscis.utils.idmaker import IdMaker, MAX_WORKER_ID
from piscis.utils.timeutil import now
from piscis.exception import NotFound
from typing import Tuple
from piscis.db.session_manager import SQLAlchemy
import os

db = SQLAlchemy()


class MixinJSONSerializer:
    @orm.reconstructor
    def init_on_load(self):
        self._fields = []
        self._exclude = []

        self._set_fields()
        self.__prune_fields()

    def _set_fields(self):
        pass

    def __prune_fields(self):
        columns = inspect(self.__class__).attrs
        if not self._fields:
            all_columns = set([column.key for column in columns])
            self._fields = list(all_columns - set(self._exclude))

    def hide(self, *args):
        for field in args:
            if isinstance(field, InstrumentedAttribute):
                self._fields.remove(field.key)
            elif isinstance(field, str):
                self._fields.remove(field)
        return self

    def set_for_display(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self._fields:
                self._fields.append(k)
                setattr(self, k, v)
        return self

    def keys(self):
        if not hasattr(self, "_fields"):
            self.init_on_load()
        return self._fields

    def __getitem__(self, key):
        return getattr(self, key)


class InfoCrud(db.Model, MixinJSONSerializer):
    __abstract__ = True
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    _model_dict = {}

    def _set_fields(self):
        self._exclude = ["deleted_at"]

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != "id":
                setattr(self, key, value)

    @property
    def table_prefix(self):
        raise NotImplementedError

    @classmethod
    def get_model(cls, dynamic_params):
        """
        用于分表
        指定__abstract__=True
        覆盖父类的table_prefix
        不指定__tablename__
        """
        table_name = f"{cls().table_prefix}_{dynamic_params}"
        if table_name not in cls._model_dict:
            new_cls = type(table_name, (cls,), {'__tablename__': table_name})
            if (prefix := id_prefix_manager.get_prefix(cls)) is not None:
                id_prefix_manager.storage(new_cls, prefix)

            cls._model_dict[table_name] = new_cls
        return cls._model_dict[table_name]

    @classmethod
    def get_session(cls, **kwargs):
        if 'session' in kwargs:
            return kwargs['session']
        else:
            return db.session

    def gen_id(self):
        id_prefix = id_prefix_manager.get_prefix(self.__class__)
        if id_prefix is None:
            return None
            # raise Exception(f'error:{self.__class__} not register prefix')
        else:
            datacenter_id = os.environ.get('DATACENTER_ID', 1)
            worker_id = os.getpid() % MAX_WORKER_ID + 1
            new_id = IdMaker(datacenter_id, worker_id).get_id()
            data = [id_prefix, self.dynamic_id_prefix(), str(new_id)]
            return '_'.join([i for i in data if i])

    def dynamic_id_prefix(self) -> str:
        """
        子类覆盖该方法，实现动态变化前缀的需求
        """
        return ''

    @classmethod
    def create(cls, **kwargs):
        """
        创建
        """
        one = cls()
        session = cls.get_session(**kwargs)
        for key in kwargs.keys():
            if hasattr(one, key):
                setattr(one, key, kwargs[key])
        if not one.id:
            one.id = one.gen_id()
        session.add(one)
        if kwargs.get("commit") is True:
            session.commit()
        return one

    def save(self, **kwargs):
        """
        创建
        """
        session = self.get_session(**kwargs)
        if not self.id:
            self.id = self.gen_id()
        session.add(self)
        if kwargs.get("commit") is True:
            session.commit()
        return self

    def update(self, **kwargs):
        """
        更新
        """
        session = self.get_session(**kwargs)
        for key in kwargs.keys():
            if hasattr(self, key):
                setattr(self, key, kwargs[key])
        session.add(self)
        if kwargs.get("commit") is True:
            session.commit()
        return self

    def delete(self, **kwargs):
        """
        逻辑删除
        """
        session = self.get_session(**kwargs)
        self.deleted_at = now()
        session.add(self)
        # 提交会话
        if kwargs.get("commit") is True:
            session.commit()

    def hard_delete(self, **kwargs):
        """
        物理删除
        """
        session = self.get_session(**kwargs)
        session.delete(self)
        # 提交会话
        if kwargs.get("commit") is True:
            session.commit()

    @classmethod
    def base_query(cls, filters: Tuple = tuple(), session=None, order_by: Tuple = None, **kwargs):
        if kwargs.get("deleted_at") is None and not kwargs.get("ignore_delete"):
            kwargs["deleted_at"] = None
        kwargs.get("ignore_delete") and kwargs.pop('ignore_delete')
        if session is None:
            query = cls.query
        else:
            query = session.query(cls)
        query = query.filter(*filters).filter_by(**kwargs)
        if order_by:
            query = query.order_by(*order_by)
        return query

    @classmethod
    def get(cls, one=True, filters: Tuple = tuple(), session=None, order_by: Tuple = None, **kwargs):
        query = cls.base_query(filters, session, order_by, **kwargs)
        if one:
            return query.first()
        return query.all()

    @classmethod
    def get_or_404(cls, one=True, filters: Tuple = tuple(), session=None, none_message=None, order_by: Tuple = None,
                   **kwargs):
        v = cls.get(one, filters, session, order_by, **kwargs)
        if not v:
            if none_message:
                raise NotFound(none_message)
            else:
                raise NotFound()
        return v

    @classmethod
    def paginate(cls, page=1, page_size=20, filters: Tuple = tuple(), session=None, order_by: Tuple = None, **kwargs):

        query = cls.base_query(filters, session, order_by, **kwargs)
        if order_by:
            query = query.order_by(*order_by)
        return query.offset((page - 1) * page_size).limit(page_size).all()


def get_total_nums(cls: "InfoCrud", condition, is_soft=False, session=None):
    db_session = session or db.session
    nums = db_session.query(func.count(cls.id))
    nums = (
        nums.filter(cls.deleted_at is None).filter(condition).scalar()
        if is_soft
        else nums.filter(condition).scalar()
    )
    if nums:
        return nums
    else:
        return 0
