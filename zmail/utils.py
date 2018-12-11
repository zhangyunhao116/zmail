"""
zmail.utils
~~~~~~~~~~~~
This module contains some useful function power zmail.
"""

import os
from typing import Optional

from .helpers import get_abs_path, make_list
from .parser import parse_mail
from .structures import CaseInsensitiveDict


def save_attachment(mail: CaseInsensitiveDict, target_path: Optional[str] = None, overwrite=False):
    """Parsing attachment and save it."""
    if mail.get('attachments'):
        if target_path is not None:
            assert os.path.isdir(target_path) and os.path.exists(target_path)
        else:
            target_path = os.getcwd()

        for name, raw in mail['attachments']:
            file_path = os.path.join(target_path, name)
            if not overwrite and os.path.exists(file_path):
                raise FileExistsError("{} already exists, set overwrite to True to avoid this error.")
            with open(file_path, 'wb') as f:
                f.write(raw)


def show(mails: list or CaseInsensitiveDict) -> None:
    """Show mail or mails."""
    mails = make_list(mails)
    for mail in mails:
        print('-------------------------')
        for k in ('subject', 'id', 'from', 'to', 'date', 'content_text', 'content_html', 'attachments'):
            if k != 'attachments':
                print(k.capitalize() + ' ', mail.get(k))
            else:
                _ = ''
                for idx, v in enumerate(mail['attachments']):
                    _ += str(idx + 1) + '.' + 'Name:' + v[0] + ' ' + 'Size:' + str(len(v[1])) + ' '

                print(k.capitalize() + ' ', _)


def read_html(html_path: str):
    """Get html content by its path."""
    path = get_abs_path(html_path)

    with open(path, 'r') as f:
        content = f.read()

    return content


def read(file_path: str, SEP=b'\r\n') -> CaseInsensitiveDict:
    """Read a mail."""
    abs_path = get_abs_path(file_path)

    with open(abs_path, 'rb') as f:
        raw_lines = f.read().split(SEP)

    return parse_mail(raw_lines, 0)


def save(mail, name=None, target_path=None, overwrite=False) -> bool:
    """Save a mail."""
    if name is None:
        name = str(mail['subject'] + '.eml') if mail.get('subject') else 'Untitled'

    if target_path is None:
        target_path = os.getcwd()

    file_path = os.path.join(target_path, name)

    if not overwrite and os.path.exists(file_path):
        raise FileExistsError("{} already exists, set overwrite to True to avoid this error.")

    with open(file_path, 'wb') as f:
        f.write(b'\r\n'.join(mail['raw']))

    return True
