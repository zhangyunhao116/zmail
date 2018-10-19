import logging

from zmail.server import MailServer

from .utils import accounts

logger = logging.getLogger('zmail')


def test_initiate_server():
    account = accounts[0]
    config = {
        'username': account[0], 'password': account[1],
        'smtp_host': 'smtp_host', 'smtp_port': 10,
        'pop_host': 'pop_host', 'pop_port': 10,
        'smtp_ssl': True, 'pop_ssl': True,
        'smtp_tls': False, 'pop_tls': False,
        'debug': False, 'log': logger, 'timeout': 30,
        'auto_add_from': False, 'auto_add_to': False
    }
    server = MailServer(**config)
    for k, v in config.items():
        assert getattr(server, k) is v
