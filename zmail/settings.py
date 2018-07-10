"""
zmail.settings
~~~~~~~~~~~~
This module contains some settings for zmail running or test.
"""

__publish__ = True

__local__ = 'zmail.local'

# Logging level: INFO == 20 , WARNING == 30 , ERROR == 40 , CRITICAL == 50
__level__ = 30 if __publish__ else 20
