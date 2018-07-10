"""
zmail.exceptions
~~~~~~~~~~~~~~~~
Include all exceptions used within zmail.
"""


class ZmailException(IOError):
    """Base exception."""


class InvalidProtocol(ZmailException, ValueError):
    """Invalid protocol settings used."""
