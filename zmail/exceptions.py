"""
zmail.exceptions
~~~~~~~~~~~~~~~~
Include all exceptions used within zmail.
"""


class ZmailException(RuntimeError):
    """Base exception."""


class InvalidProtocol(ZmailException, ValueError):
    """Invalid protocol settings used."""


class ParseError(ZmailException):
    """Parse mail error."""


class InvalidArguments(ZmailException):
    """Invalid arguments."""


class ZmailInternalError(ZmailException):
    """Internal error."""
