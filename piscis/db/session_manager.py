from sqlalchemy.orm import sessionmaker, scoped_session
from flask_sqlalchemy import SQLAlchemy as _sqlAlchemy
from contextlib import contextmanager


class SQLAlchemy(_sqlAlchemy):

    def get_session(self, bind):
        engine = self.get_engine(self.app, bind=bind)
        sess = scoped_session(sessionmaker(bind=engine))
        return sess

    @contextmanager
    def auto_commit(self, **kwargs):
        session = self.session
        if 'session' in kwargs:
            session = kwargs['session']
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
