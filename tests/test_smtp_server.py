import logging
import smtplib
from unittest import mock

import pytest

from zmail.info import get_supported_server_info
from zmail.server import SMTPServer


@pytest.fixture
def smtp_server(accounts):
    if not accounts:
        pytest.skip('Can not get accounts')

    account = accounts[0]
    username = account[0]
    password = account[1]
    config = get_supported_server_info(username)
    return SMTPServer(username, password,
                      host=config['smtp_host'],
                      port=config['smtp_port'],
                      ssl=config['smtp_ssl'],
                      tls=config['smtp_tls'],
                      timeout=60,
                      debug=False)


@pytest.fixture
def smtp_server_config(accounts):
    if not accounts:
        pytest.skip('Can not get accounts')

    account = accounts[0]
    username = account[0]
    password = account[1]
    config = get_supported_server_info(username)
    return {
        'username': username,
        'password': password,
        'host': config['smtp_host'],
        'port': config['smtp_port'],
        'ssl': config['smtp_ssl'],
        'tls': config['smtp_tls'],
        'timeout': 60,
        'debug': False
    }


def test_smtp_server_init(smtp_server_config, accounts):
    account = accounts[0]
    username = account[0]
    password = account[1]
    new_logger = mock.Mock()
    srv = SMTPServer(**smtp_server_config, log=new_logger)
    assert srv.username == username
    assert srv.password == password
    assert srv.host == smtp_server_config['host']
    assert srv.port == smtp_server_config['port']
    assert srv.ssl == smtp_server_config['ssl']
    assert srv.tls == smtp_server_config['tls']
    assert srv.timeout == 60
    assert srv.debug is False
    assert srv.log is new_logger


def test_smtp_server_default_logger(smtp_server_config):
    srv = SMTPServer(**smtp_server_config)
    assert srv.log == logging.getLogger('zmail')


def test_smtp_ssl_tls_error(smtp_server_config):
    configs = smtp_server_config.copy()
    configs.update(tls=True)
    with pytest.raises(TypeError):
        SMTPServer(**configs)


def test_smtp_make_server(smtp_server_config):
    srv = SMTPServer(**smtp_server_config)
    srv._make_server()
    assert isinstance(srv.server, (smtplib.SMTP_SSL if srv.ssl else smtplib.SMTP))


def test_smtp_login(smtp_server_config):
    srv = SMTPServer(**smtp_server_config)
    srv.login()
    assert srv.is_login() is True and srv._login is True
    srv.logout()


def test_smtp_duplicate_login(smtp_server_config):
    srv = SMTPServer(**smtp_server_config)
    srv.login()
    srv.login()
    assert srv.is_login() is True and srv._login is True
    srv.logout()


def test_smtp_logout(smtp_server_config):
    srv = SMTPServer(**smtp_server_config)
    srv.login()
    srv.logout()
    assert srv.is_login() is False and srv._login is False


def test_smtp_context(smtp_server):
    assert smtp_server.is_login() is False
    with smtp_server as server:
        assert isinstance(server, SMTPServer)
        assert server.server is not None
        assert server.is_login() is True and server._login is True
    assert server.server is None
    assert server.is_login() is False and server._login is False


def test_smtp_check_available(smtp_server_config):
    assert SMTPServer(**smtp_server_config).check_available()
    incorrect_config = smtp_server_config.copy()
    incorrect_config.update(host='')
    assert SMTPServer(**incorrect_config).check_available() is False


# Methods

def test_send_mail():
    pass
