from zmail.server import SMTPServer, POPServer
from zmail.info import get_supported_server_info, get_enterprise_server_config
from test.utils import accounts

server_default_configs = {
    'username': '',
    'password': '',
    'host': '',
    'port': 995,
    'timeout': 60,
    'ssl': True,
    'tls': False,
    'debug': True,
}

account = accounts[0]


def get_config(protocol):
    """Get specified protocol config base on username."""
    username = account[0]
    password = account[1]
    config = server_default_configs.copy()
    config.update(username=username, password=password)
    config.update({k.split('_')[1]: v for k, v in get_supported_server_info(username, protocol).items()})
    return config


def get_configs(protocol):
    configs = list()
    for _account in accounts:
        username = _account[0]
        password = _account[1]
        config = server_default_configs.copy()
        config.update(username=username, password=password)
        config.update({k.split('_')[1]: v for k, v in get_supported_server_info(username, protocol).items()})
        configs.append(config)
    return configs


def test_get_supported_server_info():
    for i in accounts:
        username = i[0]
        assert len(get_supported_server_info(username)) == 0, username
        assert len(get_supported_server_info(username, 'smtp')) == 4, username
        assert len(get_supported_server_info(username, 'smtp')) == 4, username
        assert len(get_supported_server_info(username, 'smtp', 'pop')) == 8, username
        assert len(get_supported_server_info(username, 'smtp', 'pop', 'imap')) in (8, 12), username
        # SSL and TLS can not be true together.
        j = get_supported_server_info(username, 'smtp', 'pop', 'imap')
        assert not (j['smtp_tls'] and j['smtp_ssl']), username
        assert not (j['pop_tls'] and j['pop_ssl']), username
        if j.get('imap_tls') is not None:
            assert not (j['imap_tls'] and j['imap_ssl']), username

        # PORT is INT.
        for k, v in j.items():
            if 'port' in k:
                assert isinstance(v, int), (k, v)


def test_get_enterprise_server_config():
    pass


# Test all configs working correctly
def test_all_configs():
    for config in get_configs('smtp'):
        srv = SMTPServer(**config)
        assert srv.check_available(), config['username']
    for config in get_configs('pop'):
        srv = POPServer(**config)
        assert srv.check_available(), config['username']
