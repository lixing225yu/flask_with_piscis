from datetime import datetime
from datetime import timezone

import pytz

LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo
_utc_tz = pytz.utc
_local_tz = pytz.timezone("Asia/Shanghai")


def now():
    """返回utc当前时间"""
    return _utc_tz.localize(datetime.utcnow())


def get_tz(is_utc: bool = True) -> datetime.tzinfo:
    return timezone.utc if is_utc is True else LOCAL_TIMEZONE


def format_datetime(dt: datetime, time_format: str = "%Y-%m-%d %H:%M:%S", to_local: bool = True, is_utc: bool = True) -> str:
    """
    格式化dt
    :param dt:
    :param time_format:
    :param to_local: 是否转换为本地时间。
    :param is_utc: dt是否是utc时间。如果dt有tzinfo，忽略is_utc。
    :return:
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=get_tz(is_utc=is_utc))
    if to_local:
        dt = dt.astimezone(tz=LOCAL_TIMEZONE)
    return dt.strftime(time_format)


def to_datetime(dt_str, format="%Y-%m-%d %H:%M:%S", utc=False):
    """
    utc: False 按当前时区解析，True 按UTC解析
    """
    try:
        dt = datetime.strptime(dt_str, format)
        return _utc_tz.localize(dt) if utc else _local_tz.localize(dt)
    except Exception:
        return None


def to_local(dt):
    return dt.astimezone(tz=LOCAL_TIMEZONE)


if __name__ == '__main__':
    print(to_local(datetime.now()))