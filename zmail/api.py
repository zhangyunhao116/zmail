"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""

from .server import MailServer


def server(user, password):
    """A shortcut to use MailServer.

    SMTP:
        server.send_mail([recipient,], mail)

    POP3:
        server.get_mail(which)
        server.get_mails(subject, from, after, before)
        server.get_latest()
        server.get_all_info()
    """
    return MailServer(user, password)
