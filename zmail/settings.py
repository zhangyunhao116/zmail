"""
zmail.settings
~~~~~~~~~~~~
This module contains some settings for zmail running or test.
"""

__status__ = 'publish'

__local__ = 'zmail.local'

# Logging level: INFO == 20 , WARNING == 30 , ERROR == 40 , CRITICAL == 50
__level__ = 20 if __status__ == 'dev' else 30
