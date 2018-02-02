"""
zmail.__init__
~~~~~~~~~~~~
Zmail allows you to send and get email as possible as it can be.

"""
import logging
from .api import encode_mail, decode_mail, server

__status__ = 'publish'

# Define logger.
logger = logging.getLogger('zmail')

sh = logging.StreamHandler()
fmt = logging.Formatter('[%(levelname)s] %(message)s')
sh.setFormatter(fmt)
logger.addHandler(sh)

logging_level = logging.INFO if __status__ == 'dev' else logging.WARNING
logger.setLevel(logging_level)

if __name__ == "__main__":
    pass
