import pytest

from zmail.info import (DEFAULT_SERVER_CONFIG,
                        SUPPORTED_ENTERPRISE_SERVER_CONFIG, SUPPORTED_SERVER,
                        get_supported_server_info)


def test_supported_server():
    assert isinstance(SUPPORTED_SERVER, dict)
    assert isinstance(SUPPORTED_ENTERPRISE_SERVER_CONFIG, dict)

    combine = SUPPORTED_SERVER.copy()
    combine.update(SUPPORTED_ENTERPRISE_SERVER_CONFIG)

    for host in combine:
        host_info = combine[host]
        smtp_host = host_info['smtp_host']
        smtp_port = host_info['smtp_port']
        smtp_ssl = host_info['smtp_ssl']
        smtp_tls = host_info['smtp_tls']
        pop_host = host_info['pop_host']
        pop_port = host_info['pop_port']
        pop_ssl = host_info['pop_ssl']
        pop_tls = host_info['pop_tls']

        assert isinstance(smtp_host, str), smtp_host
        assert isinstance(pop_host, str), pop_host

        assert isinstance(smtp_port, int)
        assert isinstance(pop_port, int)

        assert not (smtp_ssl and smtp_tls)
        assert not (pop_ssl and pop_tls)


def test_get_supported_server_info():
    for k in SUPPORTED_SERVER:
        assert get_supported_server_info('zmailtest@' + k), SUPPORTED_SERVER[k]


def test_get_supported_server_info_as_enterprise_server():
    for k in SUPPORTED_ENTERPRISE_SERVER_CONFIG:
        assert get_supported_server_info('zmailtest@gmail.com', config=k), SUPPORTED_ENTERPRISE_SERVER_CONFIG[k]

    with pytest.raises(RuntimeError):
        get_supported_server_info('zmailtest@gmail.com', config='zmailtest')


def test_get_supported_server_info_as_default_config():
    assert get_supported_server_info('zmailtest@zmailtest.com'), DEFAULT_SERVER_CONFIG
