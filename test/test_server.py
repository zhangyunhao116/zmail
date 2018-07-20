import zmail
from zmail.server import MailServer


def test_server_isinstance():
    server = zmail.server('test', 'test')
    assert isinstance(server, MailServer), True
