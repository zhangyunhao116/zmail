import datetime
import os
import re
from typing import Optional

from .exceptions import InvalidArguments
from .structures import CaseInsensitiveDict

DATETIME_PATTERN = re.compile(r'([0-9]+)?-?([0-9]{1,2})?-?([0-9]+)?\s*([0-9]{1,2})?:?([0-9]{1,2})?:?([0-9]{1,2})?\s*')


def convert_date_to_datetime(_date: str or datetime.datetime) -> datetime.datetime:
    """Convert date like '2018-1-1 12:00:00 to datetime object.'"""
    if isinstance(_date, datetime.datetime):
        # Shortcut
        return _date

    _match_info = DATETIME_PATTERN.fullmatch(_date)
    if _match_info is not None:
        year, month, day, hour, minute, second = [int(i) if i is not None else None for i in _match_info.groups()]
    else:
        raise InvalidArguments('Invalid date format ' + str(_date))

    if None in (year, month, day):
        now = datetime.datetime.now()
        year = year or now.year
        month = month or now.month
        day = day or now.day
    if None in (hour, minute, second):
        hour = hour or 0
        minute = minute or 0
        second = second or 0

    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)


def match_conditions(mail_headers: CaseInsensitiveDict,
                     subject: Optional[str] = None,
                     start_time: Optional[datetime.datetime] = None,
                     end_time: Optional[datetime.datetime] = None,
                     sender: Optional[str] = None) -> bool:
    """Match all conditions."""
    mail_subject = mail_headers.get('subject')  # type:str or None
    mail_sender = mail_headers.get('from')  # type:str or None
    mail_date = mail_headers.get('date')  # type: datetime.datetime or None

    if subject is not None:
        if mail_subject is None or subject not in mail_subject:
            return False

    if sender is not None:
        if mail_sender is None or sender not in mail_sender:
            return False

    if start_time is not None:
        if mail_date is None or start_time > mail_date:
            return False

    if end_time is not None:
        if mail_date is None or end_time < mail_date:
            return False

    return True


def get_intersection(main_range: tuple, sub_range: tuple) -> list:
    main_start, main_end = main_range
    sub_start, sub_end = sub_range

    if main_start > main_end:
        return list()

    if sub_start is None or sub_start < main_start:
        sub_start = main_start
    if sub_end is None or sub_end > main_end:
        sub_end = main_end

    main_set = {i for i in range(main_start, main_end + 1)}
    sub_set = {i for i in range(sub_start, sub_end + 1)}

    return sorted(tuple((main_set & sub_set)))


def make_iterable(obj) -> list or tuple:
    """Get an iterable obj."""
    return obj if isinstance(obj, (tuple, list)) else (obj,)


def get_abs_path(file: str) -> str:
    """if the file exists, return its abspath or raise a exception."""
    if os.path.exists(file):
        return file

    # Assert file exists in currently directory.
    work_path = os.path.abspath(os.getcwd())

    if os.path.exists(os.path.join(work_path, file)):
        return os.path.join(work_path, file)
    else:
        raise FileExistsError("The file %s doesn't exist." % file)
