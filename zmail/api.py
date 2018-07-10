"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""
import logging

from .server import MailServer
from .message import mail_decode
from .utils import get_attachment, get_html, show, read, save
from .info import get_enterprise_server_config

logger = logging.getLogger('zmail')

# Backward-compatible with earlier versions.
read_eml = read
save_eml = save

__all__ = ['get_attachment', 'get_html', 'show', 'read', 'save', 'server', 'decode', 'read_eml', 'save_eml']


def server(user, password, smtp_host=None, smtp_port=None, pop_host=None, pop_port=None, smtp_ssl=None, pop_ssl=None,
           smtp_tls=None, pop_tls=None, config=None, timeout=60, auto_add_to=True, auto_add_from=True):
    """A wrapper to MailServer.

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
        config_dict = get_enterprise_server_config(config)
        if config_dict:
            return MailServer(user, password, **config_dict, timeout=timeout, auto_add_to=auto_add_to,
                              auto_add_from=auto_add_from)
        else:
            logger.warning('User-defined server config error, use default config instead.')

    return MailServer(**{k: v for k, v in locals().items() if k not in ('config_dict', 'config')})


def decode(mail_as_bytes, which=1):
    """Decode bytes mail, as usual in your disk."""
    return mail_decode(mail_as_bytes, which)
