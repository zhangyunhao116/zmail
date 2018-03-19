"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""

from .server import MailServer
from .utils import get_attachment, get_html, show, read_eml, save_eml
from .message import mail_decode


def server(user, password, smtp_host=None, smtp_port=None, pop_host=None, pop_port=None, smtp_ssl=None, pop_ssl=None):
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
    return MailServer(user, password, smtp_host=smtp_host, smtp_port=smtp_port, pop_host=pop_host, pop_port=pop_port,
                      smtp_ssl=smtp_ssl,
                      pop_ssl=pop_ssl)


def decode(mail_as_bytes, which=1):
    return mail_decode(mail_as_bytes, which)
