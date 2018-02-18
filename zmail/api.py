"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""

from .server import MailServer
from .utils import get_attachment, show


def server(user, password):
    """A shortcut to use MailServer.

    SMTP:
        server.send_mail([recipient,], mail)

    POP3:
        server.get_mail(which)
        server.get_mails(subject, sender, after, before)
        server.get_latest()
        server.get_info()
        server.stat()


    Parse mail:
        server.show(mail)
        server.get_attachment(mail)
    """
    return MailServer(user, password)
