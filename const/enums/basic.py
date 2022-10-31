from piscis.core.fieldenum import FieldEnum, T


class UserTypeEnum(FieldEnum):
    """合作方类型"""

    Admin = T(1, "管理员")
    Normal = T(2, "普通员工")
