"""
zmail.info
~~~~~~~~~~
This module provide supported server information.


'Server_provider_address':{
    'protocol':('protocol_server_address', port, use_ssl,use_tls),
}
"""
SUPPORTED_SERVER = {
    '163.com': {
        'smtp': ('smtp.163.com', 994, True, False),
        'pop3': ('pop.163.com', 995, True, False),
        'imap': ('imap.163.com', 993, True, False)

    },
    '126.com': {
        'smtp': ('smtp.126.com', 994, True, False),
        'pop3': ('pop.126.com', 995, True, False),
        'imap': ('imap.126.com', 993, True, False)

    },
    'yeah.net': {
        'smtp': ('smtp.yeah.net', 994, True, False),
        'pop3': ('pop.yeah.net', 995, True, False),
        'imap': ('imap.yeah.net', 993, True, False)

    },
    'qq.com': {
        'smtp': ('smtp.qq.com', 465, True, False),
        'pop3': ('pop.qq.com', 995, True, False),
    },
    'gmail.com': {
        'smtp': ('smtp.gmail.com', 587, False, True),
        'pop3': ('pop.gmail.com', 995, True, False),
    },
    'sina.com': {
        'smtp': ('smtp.sina.com', 465, True, False),
        'pop3': ('pop.sina.com', 995, True, False),
    },
    'outlook.com': {
        'smtp': ('smtp-mail.outlook.com', 587, False, True),
        'pop3': ('pop.outlook.com', 995, True, False),
    },
    'hotmail.com': {
        'smtp': ('smtp.office365.com', 587, False, True),
        'pop3': ('outlook.office365.com', 995, True, False),
    },
}

SUPPORTED_ENTERPRISE_SERVER_CONFIG = {
    'qq': {
        'smtp_host': 'smtp.exmail.qq.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.exmail.qq.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False

    },
    'ali': {
        'smtp_host': 'smtp.mxhichina.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop3.mxhichina.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False
    },

}


def get_supported_server_info(mail_address: str, protocol: str) -> tuple:
    """Use user address to get server address and port.

    :param mail_address: str
    :param protocol: str
    :return: ('protocol_server_address', port, use_ssl)
    """
    provider = mail_address.split('@')[1]

    if provider in SUPPORTED_SERVER:
        server_info = SUPPORTED_SERVER[provider]
        if protocol in server_info:
            return server_info[protocol]

    if protocol == 'smtp':
        return 'smtp.' + provider, 465, True, False
    elif protocol == 'pop3':
        return 'pop3.' + provider, 995, True, False


def get_enterprise_server_config(config: str):
    """Get user-defined config.
    :param config: str
    :return: ('protocol_server_address', port, use_ssl)
    """
    if config in SUPPORTED_ENTERPRISE_SERVER_CONFIG:
        return SUPPORTED_ENTERPRISE_SERVER_CONFIG[config]
    return False
