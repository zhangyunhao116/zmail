"""
zmail.__init__
~~~~~~~~~~~~
Zmail allows you to send and get email as possible as it can be.
"""
import logging
from .api import *
from .settings import __level__

# Define logger.
logger = logging.getLogger('zmail')

sh = logging.StreamHandler()
fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh.setFormatter(fmt)
logger.addHandler(sh)

logger.setLevel(__level__)

# A standard zmail dict.
MAIL = {
    'subject': 'Zmail',  # Anything you want.
    'content': 'This message from zmail!',  # Anything you want.
    'attachments': '',  # Absolute path will be better.
}
