import datetime
import os
import re
from typing import Optional

from .exceptions import InvalidArguments
from .structures import CaseInsensitiveDict

DATETIME_PATTERN = re.compile(r'([0-9]+)?-?([0-9]{1,2})?-?([0-9]+)?\s*([0-9]{1,2})?:?([0-9]{1,2})?:?([0-9]{1,2})?\s*')


def convert_date_to_datetime(_date: str) -> datetime.datetime:
    """Convert date like '2018-1-1 12:00:00 to datetime object.'"""
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
                     after: Optional[str or datetime.datetime] = None,
                     before: Optional[str or datetime.datetime] = None,
                     sender: Optional[str] = None) -> bool:
    """Match all conditions."""
    _subject = mail_headers.get('subject')  # type:str or None
    _sender = mail_headers.get('from')  # type:str or None
    _date = mail_headers.get('date')  # type: datetime.datetime or None

    if None not in (subject, _subject) and _subject.find(subject) == -1:
        return False

    if None not in (sender, _sender) and _sender.find(sender) == -1:
        return False

    if None not in (before, _date):
        if isinstance(before, str):
            before_as_datetime = convert_date_to_datetime(before)
        elif isinstance(before, datetime.datetime):
            before_as_datetime = before
        else:
            raise InvalidArguments('before excepted type str or datetime.datetime got {}'.format(type(before)))

        if before_as_datetime < _date:
            return False

    if None not in (after, _date):
        if isinstance(after, str):
            after_as_datetime = convert_date_to_datetime(after)
        elif isinstance(after, datetime.datetime):
            after_as_datetime = after
        else:
            raise InvalidArguments('after excepted type str or datetime.datetime got {}'.format(type(after)))

        if _date is None or after_as_datetime > _date:
            return False

    return True


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
