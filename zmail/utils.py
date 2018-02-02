"""
zmail.utils
~~~~~~~~~~~~
This module contains some useful function power zmail.
"""

import os


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
