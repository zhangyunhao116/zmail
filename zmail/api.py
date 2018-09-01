"""
zmail.api
~~~~~~~~~~~~
This module implements the zmail API.
"""
import logging

from .server import MailServer
from .message import mail_decode
from .utils import get_attachment, get_html, show, read, save
from .info import get_enterprise_server_config, get_supported_server_info

logger = logging.getLogger('zmail')

# Backward-compatible with earlier versions.
read_eml = read
save_eml = save

__all__ = ['get_attachment', 'get_html', 'show', 'read', 'save', 'server', 'decode', 'read_eml', 'save_eml']


def server(username, password, smtp_host=None, smtp_port=None, pop_host=None, pop_port=None, smtp_ssl=None,
           pop_ssl=None,
           smtp_tls=None, pop_tls=None, config=None, timeout=60, debug=False, auto_add_to=True, auto_add_from=True):
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

    user_define_config = {
        'smtp_host': smtp_host,
        'smtp_port': smtp_port,
        'smtp_ssl': smtp_ssl,
        'smtp_tls': smtp_tls,
        'pop_host': pop_host,
        'pop_port': pop_port,
        'pop_ssl': pop_ssl,
        'pop_tls': pop_tls,
    }

    if config:
        config_dict = get_enterprise_server_config(config)
        if config_dict:
            config_dict.update({k: v for k, v in user_define_config.items() if v is not None})
            return MailServer(username, password, **config_dict, timeout=timeout, debug=debug,
                              auto_add_to=auto_add_to, auto_add_from=auto_add_from)
        else:
            logger.warning('User-defined server config error, use default config instead.')

    # Load default configs.
    config_dict = get_supported_server_info(username, 'smtp', 'pop')
    config_dict.update({k: v for k, v in user_define_config.items() if v is not None})
    return MailServer(username, password, **config_dict, timeout=timeout, debug=debug,
                      auto_add_to=auto_add_to, auto_add_from=auto_add_from)


def decode(mail_as_bytes, which=1):
    """Decode bytes mail, as usual in your disk."""
    return mail_decode(mail_as_bytes, which)
