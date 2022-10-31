from pydantic.errors import *
from pydantic.errors import SetMinLengthError, SetMaxLengthError


def patch():
    MissingError.msg_template = "必填项不能为空"  # field required
    DictError.msg_template = "字典格式不正确"  # value is not a valid dict
    EmailError.msg_template = "邮箱格式不正确"  # value is not a valid email address
    IntegerError.msg_template = "整数格式不正确"  # value is not a valid integer"
    FloatError.msg_template = "浮点数格式不正确"  # value is not a valid float
    DecimalError.msg_template = "浮点数格式不正确"  # value is not a valid decimal
    DecimalIsNotFiniteError.msg_template = "浮点数格式不正确"  # value is not a valid decimal
    NumberNotGtError.msg_template = "数字须大于 {limit_value}"  # ensure this value is greater than {limit_value}
    NumberNotGeError.msg_template = "数字须大于等于 {limit_value}"  # ensure this value is greater than or equal to {limit_value}
    NumberNotLtError.msg_template = "数字须小于 {limit_value}"  # ensure this value is less than {limit_value}
    NumberNotLeError.msg_template = "数字须小于等于 {limit_value} "  # ensure this value is less than or equal to {limit_value}

    StrictBoolError.msg_template = "布尔格式不正确"  # value is not a valid boolean
    DateTimeError.msg_template = "时间格式不正确"  # invalid datetime format
    DateError.msg_template = "日期格式不正确"  # invalid date format
    TimeError.msg_template = "时间格式不正确"  # invalid time format
    JsonError.msg_template = "JSON格式不合法"  # Invalid JSON

    StrError.msg_template = "请输入字符串"  # str type expected
    AnyStrMinLengthError.msg_template = "至少包含 {limit_value} 个字符"
    AnyStrMaxLengthError.msg_template = "最多不能超过 {limit_value} 个字符"

    ListError.msg_template = "列表格式不正确"  # value is not a valid list
    ListMinLengthError.msg_template = "至少包含 {limit_value} 项"  # ensure this value has at least {limit_value} items
    ListMaxLengthError.msg_template = "最多不能超过 {limit_value} 项 "  # ensure this value has at most {limit_value} items

    SetError.msg_template = "集合格式不正确"  # value is not a valid set
    SetMinLengthError.msg_template = "至少包含 {limit_value} 项"  # ensure this value has at least {limit_value} items
    SetMaxLengthError.msg_template = "最多不能超过 {limit_value} 项 "  # ensure this value has at most {limit_value} items

    WrongConstantError.__str__ = lambda x: '值范围不合法'  # f'unexpected value; permitted: {permitted}'
