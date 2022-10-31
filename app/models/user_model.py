from piscis.core.wrappers import id_prefix_manager
from piscis.db.database import InfoCrud as Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text


@id_prefix_manager.register('u')
class UserModel(Base):
    __tablename__ = 'user'

    id = Column(String, primary_key=True)
    name = Column(String(128), nullable=False, comment="姓名")
    phone = Column(String(128), comment="姓名")
