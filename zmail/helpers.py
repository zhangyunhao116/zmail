import datetime
import os
import re
from base64 import b64encode
from typing import Optional

from .exceptions import InvalidArguments, ZmailInternalError
from .structures import CaseInsensitiveDict

DATETIME_PATTERN = re.compile(r'([0-9]+)?-?([0-9]{1,2})?-?([0-9]+)?\s*([0-9]{1,2})?:?([0-9]{1,2})?:?([0-9]{1,2})?\s*')
LOCAL_TIMEZONE = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
HDR_PREV = '=?utf-8?b?'
HDR_END = '?='


def convert_date_to_datetime(_date: str or datetime.datetime) -> datetime.datetime:
    """Convert date like '2018-1-1 12:00:00' to datetime object."""
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

    return datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second,
                             tzinfo=LOCAL_TIMEZONE)


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


def encode_mail_header(s: str) -> str:
    if not s:
        return ''
    return HDR_PREV + b64encode(s.encode('utf-8')).decode('ascii') + HDR_END


def make_list(obj) -> list:
    return obj if isinstance(obj, list) else [obj]


def make_address_header(address_list: list) -> str:
    """Used for make 'To' 'Cc' 'From' header."""
    res = []
    for address in address_list:
        if isinstance(address, tuple):
            assert len(address) == 2, 'Only two arguments!'
            name, rel_address = address
            res.append(encode_mail_header(name) + ' ' + '<{}>'.format(rel_address))
        elif isinstance(address, str):
            res.append('<{}>'.format(address))
        else:
            raise InvalidArguments('Email address can only be tuple or str.Get {} instead.'.format(type(address)))

    return ', '.join(res)


def first_not_none(*args):
    """Return first arguments which is not None."""
    for k in args:
        if k is not None:
            return k
    raise ZmailInternalError('All arguments is None!')


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
