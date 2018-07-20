import zmail
from test.base import config

server_list = [zmail.server(i[0], i[1]) for i in config]


def test_smtp_able():
    for server in server_list:
        assert server.smtp_able(), True

