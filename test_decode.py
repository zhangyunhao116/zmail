"""
test_decode
~~~~~~~~~~~~~~
Do not use.
This module test zmail decode function..
"""
import zmail.message

import os
import re


def get_specified_file(file_names, *args):
    """Get specified filename extension from a list of file names."""
    specified_filename = []

    if args is ():
        raise Exception('get_specified_file() missing at least 1 required specified argument')

    for name in file_names:
        for extension in args:
            if re.fullmatch(r'.+\.%s' % extension, name):
                specified_filename.append(name)
                break

    return specified_filename


eml_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test')

eml_list = get_specified_file(os.listdir(eml_path), 'eml')

emails = []

for i in eml_list:
    emails.append(os.path.join(eml_path, i))

for i in emails:
    mail_as_bytes = zmail.read_eml(i)
    a = zmail.decode(mail_as_bytes, 1)
    zmail.show(a)

