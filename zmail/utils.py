"""
zmail.utils
~~~~~~~~~~~~
This module contains some useful function power zmail.
"""

import os
import sys


def bytes_to_string(bytes_list):
    """Decode a list of bytes-objects to a list of string-objects."""
    return tuple(map(lambda x: x.decode(), bytes_list))


def type_check(_types, *args):
    """Each args must be a type in _types or raise a TypeError."""
    for obj in args:
        if not isinstance(obj, _types):
            raise TypeError('Parameter {} must be {}'.format(obj, _types))


def get_abs_path(file):
    """if the file exists, return its abspath or raise a exception."""
    work_path = os.path.abspath(os.getcwd())
    if os.path.isfile(os.path.join(work_path, file)):
        return os.path.join(work_path, file)
    elif os.path.isfile(file):
        return file
    else:
        raise Exception("The file %s doesn't exist." % file)


def make_iterable(obj):
    """Get a iterable obj."""
    if isinstance(obj, (tuple, list)):
        return obj
    return obj,


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


def show(mails):
    """Show mails."""
    mails = make_iterable(mails)
    for mail in mails:
        print('-------------------------')
        for k, v in mail.items():
            print(k, v)


def str_decode(text, coding=None):
    """Decode bytes to string."""
    if isinstance(text, str):
        return text
    elif isinstance(text, bytes):
        if coding:
            return text.decode(coding)
        else:
            return text.decode()
    else:
        raise Exception('String decoding error:%s' % text)


def get_html(html_path):
    """Get html content by its path."""
    path = get_abs_path(html_path)

    with open(path, 'r') as f:
        content = f.read()

    return content


def read_eml(path):
    abs_path = get_abs_path(path)
    with open(abs_path, 'rb') as f:
        result = []
        for i in f.readlines():
            if i[-2:] == b'\r\n':
                result.append(i[:-2])
    return result


def save_eml(mail, name=None, path=None):
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
