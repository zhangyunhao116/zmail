import zmail
from test.base import config

server_list = [zmail.server(i[0], i[1]) for i in config]


def test_pop_able():
    for server in server_list:
        assert server.pop_able(), True


def test_pop_stat():
    for server in server_list:
        assert isinstance(server.stat(), tuple), True


def test_get_latest_mail():
    for server in server_list:
        try:
            server.get_latest()
        except Exception as e:
            pass


def test_get_mail():
    for server in server_list:
        try:
            server.get_mail(1)
        except Exception as e:
            pass


def test_get_mails():
    for server in server_list:
        server.get_mails(subject='test', before='2019-1-1', after='2018-1-1')
