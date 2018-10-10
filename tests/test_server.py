import pytest
import smtplib
import poplib

from zmail.server import SMTPServer, POPServer
from tests.test_info import get_config, server_default_configs

srvs = (SMTPServer, POPServer)


def test_server_init():
    for i in srvs:
        srv = i(**server_default_configs)
        assert srv.username == server_default_configs['username'] \
               and srv.password == server_default_configs['password'] \
               and srv.host == server_default_configs['host'] \
               and srv.port == server_default_configs['port'] \
               and srv.timeout == server_default_configs['timeout'] \
               and srv.ssl == server_default_configs['ssl'] \
               and srv.debug == server_default_configs['debug']


def test_ssl_tls_error():
    for i in srvs:
        configs = server_default_configs.copy()
        configs.update(tls=True)
        with pytest.raises(TypeError):
            srv = i(**configs)


def test_smtp_make_server():
    srv = SMTPServer(**get_config('smtp'))
    srv._make_server()
    assert isinstance(srv.server, (smtplib.SMTP_SSL if srv.ssl else smtplib.SMTP)), \
        'test_smtp_make_server'


def test_pop_make_server():
    srv = POPServer(**get_config('pop'))
    srv._make_server()
    assert isinstance(srv.server, (poplib.POP3_SSL if srv.ssl else poplib.POP3)), \
        'test_pop_make_server'


def test_smtp_login():
    srv = SMTPServer(**get_config('smtp'))
    srv.login()
    assert srv._login is True
    assert srv.is_login() is True
    assert isinstance(srv.server, (smtplib.SMTP_SSL if srv.ssl else smtplib.SMTP))
    srv.logout()


def test_pop_login():
    srv = POPServer(**get_config('pop'))
    srv.login()
    assert srv._login is True
    assert srv.is_login() is True
    assert isinstance(srv.server, (poplib.POP3_SSL if srv.ssl else poplib.POP3))
    srv.logout()


def test_smtp_context():
    srv = SMTPServer(**get_config('smtp'))

    with srv as server:
        assert isinstance(server, SMTPServer)
        assert srv.server is not None

    assert srv.server is None


def test_check_available():
    assert SMTPServer(**get_config('smtp')).check_available()
    assert POPServer(**get_config('pop')).check_available()
    incorrect_config = get_config('smtp')
    incorrect_config.update(host='')
    assert SMTPServer(**incorrect_config).check_available() is False
    incorrect_config = get_config('pop')
    incorrect_config.update(host='')
    assert POPServer(**incorrect_config).check_available() is False


def test_pop_context():
    srv = POPServer(**get_config('pop'))

    with srv as server:
        assert isinstance(server, POPServer)
        assert srv.server is not None

    assert srv.server is None


"""Test specified smtp functions"""


def test_smtp_send_mail():
    pass
