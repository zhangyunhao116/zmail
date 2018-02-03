"""
zmail.settings
~~~~~~~~~~~~
This module contains some settings for zmail running or test.
"""
import logging

__status__ = 'publish'

# Logging level: INFO == 20 , WARNING == 30 , ERROR == 40 , CRITICAL == 50
__level__ = logging.INFO if __status__ == 'dev' else logging.WARNING
