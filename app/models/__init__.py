from sqlalchemy import Column, String

from piscis.core.wrappers import id_prefix_manager
from piscis.db.database import InfoCrud as Base


@id_prefix_manager.register("FG")
class FamilyGroup(Base):
    __tablename__ = "family_group"

    id = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False, comment='家庭组名称')


@id_prefix_manager.register("FM")
class FamilyMember(Base):
    __tablename__ = "family_member"
    id = Column(String(32), primary_key=True)
    group_id = Column(String(32), nullable=False, comment="家庭组id")
    name = Column(String(32), nullable=False, comment="学生姓名")
    passport = Column(String(32), nullable=False, unique=True, comment="学生护照号")
    birthday = Column(String(32), comment='学生出生日期')
