"""
zmail.utils
~~~~~~~~~~~~
This module contains some useful function power zmail.
"""

import os
import sys

from .helpers import get_abs_path, make_iterable
from .structures import CaseInsensitiveDict


def get_attachment(mail, *args):
    """Parsing attachment and save it."""
    names = list(args)
    names.reverse()
    if mail['attachments']:
        for attachment in mail['attachments']:
            info = attachment[0].split(';')
            name = info[0]
            body_type = info[1]
            is_text_file = True if body_type.find('text/plain') > -1 else False

            try:
                name = names.pop()
            except IndexError:
                pass

            # Write file.
            if not is_text_file:
                # Binary file.
                body = b''.join(attachment[1:])
                with open(name, 'wb') as f:
                    f.write(body)
            else:
                # Text file.
                body = tuple(map(lambda x: x.decode() + '\r\n', attachment[1:]))
                with open(name, 'w') as f:
                    f.writelines(body)


def show(mails: list or CaseInsensitiveDict):
    """Show mails."""
    mails = make_iterable(mails)
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


def get_html(html_path):
    """Get html content by its path."""
    path = get_abs_path(html_path)

    with open(path, 'r') as f:
        content = f.read()

    return content


def read(path):
    abs_path = get_abs_path(path)
    with open(abs_path, 'rb') as f:
        result = []
        for i in f.readlines():
            if i[-2:] == b'\r\n':
                result.append(i[:-2])
    return result


def save(mail, name=None, path=None):
    """Save a mail."""
    file_name = name if name else str(mail['subject'] + '.eml')
    file_path = path if path else os.path.abspath(os.path.dirname(sys.argv[0]))

    # Check if filename is empty, use date instead.
    if file_name == '.eml':
        file_name = str(mail['date'] + '.eml')

    file_locate = os.path.join(file_path, file_name)

    with open(file_locate, 'wb+') as f:
        for i in mail['raw']:
            f.write(i + b'\r\n')

    return True
