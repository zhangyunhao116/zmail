"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""
import logging

from .server import MailServer
from .message import mail_decode
from .utils import get_attachment, get_html, show, read_eml, save_eml
from .info import get_server_config

logger = logging.getLogger('zmail')

__all__ = ['get_attachment', 'get_html', 'show', 'read_eml', 'save_eml', 'server', 'decode']


def server(user, password, smtp_host=None, smtp_port=None, pop_host=None, pop_port=None, smtp_ssl=None, pop_ssl=None,
           config=None):
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
    if config:
        config_dict = get_server_config(config)
        if config_dict:
            return MailServer(user, password, **config_dict)
        else:
            logger.warning('User-defined server config error, use default config instead.')
    return MailServer(user, password, smtp_host=smtp_host, smtp_port=smtp_port, pop_host=pop_host, pop_port=pop_port,
                      smtp_ssl=smtp_ssl,
                      pop_ssl=pop_ssl)


def decode(mail_as_bytes, which=1):
    return mail_decode(mail_as_bytes, which)
