from .message import MailMessage
from .server import MailServer


def encode_mail(message):
    """A shortcut to convert a dict to a MIME obj."""
    return MailMessage().encode(message)


def decode_mail(message):
    """A shortcut to convert a MIME string to a dict."""
    return MailMessage().decode()


def server(user, password):
    """A shortcut to use MailServer."""
    return MailServer(user, password)
