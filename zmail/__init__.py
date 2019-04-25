"""
zmail.__init__
~~~~~~~~~~~~
Zmail allows you to send and get email as possible as it can be.
"""
import logging

from .api import *  # noqa
from .settings import __level__  # noqa

# Define logger.
logger = logging.getLogger('zmail')

sh = logging.StreamHandler()
fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh.setFormatter(fmt)
logger.addHandler(sh)

logger.setLevel(logging.DEBUG)

# A standard zmail dict.
MAIL = {
    'subject': 'Zmail',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '',  # Absolute path will be better.
}
