import logging
import poplib
from unittest import mock

import pytest
from zmail.info import get_supported_server_info
from zmail.server import POPServer

from tests.utils import accounts


@pytest.fixture
def pop_server():
    account = accounts[0]
    username = account[0]
    password = account[1]
    config = get_supported_server_info(username)
    return POPServer(username, password,
                     host=config['pop_host'],
                     port=config['pop_port'],
                     ssl=config['pop_ssl'],
                     tls=config['pop_tls'],
                     timeout=60,
                     debug=False)


@pytest.fixture
def pop_server_config():
    account = accounts[0]
    username = account[0]
    password = account[1]
    config = get_supported_server_info(username)
    return {
        'username': username,
        'password': password,
        'host': config['pop_host'],
        'port': config['pop_port'],
        'ssl': config['pop_ssl'],
        'tls': config['pop_tls'],
        'timeout': 60,
        'debug': False
    }


def test_pop_server_init(pop_server_config):
    account = accounts[0]
    username = account[0]
    password = account[1]
    new_logger = mock.Mock()
    srv = POPServer(**pop_server_config, log=new_logger)
    assert srv.username == username
    assert srv.password == password
    assert srv.host == pop_server_config['host']
    assert srv.port == pop_server_config['port']
    assert srv.ssl == pop_server_config['ssl']
    assert srv.tls == pop_server_config['tls']
    assert srv.timeout == 60
    assert srv.debug is False
    assert srv.log is new_logger


def test_pop_server_default_logger(pop_server_config):
    srv = POPServer(**pop_server_config)
    assert srv.log == logging.getLogger('zmail')


def test_pop_ssl_tls_error(pop_server_config):
    configs = pop_server_config.copy()
    configs.update(tls=True)
    with pytest.raises(TypeError):
        srv = POPServer(**configs)


def test_pop_make_server(pop_server_config):
    srv = POPServer(**pop_server_config)
    srv._make_server()
    assert isinstance(srv.server, (poplib.POP3_SSL if srv.ssl else poplib.POP3))


def test_pop_login(pop_server_config):
    srv = POPServer(**pop_server_config)
    srv.login()
    assert srv.is_login() is True and srv._login is True
    srv.logout()


def test_pop_duplicate_login(pop_server_config):
    srv = POPServer(**pop_server_config)
    srv.login()
    srv.login()
    assert srv.is_login() is True and srv._login is True
    srv.logout()


def test_pop_logout(pop_server_config):
    srv = POPServer(**pop_server_config)
    srv.login()
    srv.logout()
    assert srv.is_login() is False and srv._login is False


def test_pop_context(pop_server):
    assert pop_server.is_login() is False
    with pop_server as server:
        assert isinstance(server, POPServer)
        assert server.server is not None
        assert server.is_login() is True and server._login is True
    assert server.server is None
    assert server.is_login() is False and server._login is False


def test_check_available(pop_server_config):
    assert POPServer(**pop_server_config).check_available()
    incorrect_config = pop_server_config.copy()
    incorrect_config.update(host='')
    assert POPServer(**incorrect_config).check_available() is False
