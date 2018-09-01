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
        'smtp_host': 'smtp.163.com',
        'smtp_port': 994,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.163.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
        'imap_host': 'imap.163.com',
        'imap_port': 993,
        'imap_ssl': True,
        'imap_tls': False
    },
    '126.com': {
        'smtp_host': 'smtp.126.com',
        'smtp_port': 994,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.126.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
        'imap_host': 'imap.126.com',
        'imap_port': 993,
        'imap_ssl': True,
        'imap_tls': False
    },
    'yeah.net': {
        'smtp_host': 'smtp.yeah.net',
        'smtp_port': 994,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.yeah.net',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
        'imap_host': 'imap.yeah.net',
        'imap_port': 993,
        'imap_ssl': True,
        'imap_tls': False
    },
    'qq.com': {
        'smtp_host': 'smtp.qq.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.qq.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
    },
    'gmail.com': {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'pop_host': 'pop.gmail.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
    },
    'sina.com': {
        'smtp_host': 'smtp.sina.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'smtp_tls': False,
        'pop_host': 'pop.sina.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
    },
    'outlook.com': {
        'smtp_host': 'smtp-mail.outlook.com',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'pop_host': 'pop.outlook.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
    },
    'hotmail.com': {
        'smtp_host': 'smtp.office365.com',
        'smtp_port': 587,
        'smtp_ssl': False,
        'smtp_tls': True,
        'pop_host': 'outlook.office365.com',
        'pop_port': 995,
        'pop_ssl': True,
        'pop_tls': False,
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

DEFAULT_SERVER_CONFIG = {
    'smtp_host': 'smtp.',
    'smtp_port': 465,
    'smtp_ssl': True,
    'smtp_tls': False,
    'pop_host': 'pop.',
    'pop_port': 995,
    'pop_ssl': True,
    'pop_tls': False,
    'imap_host': 'imap.',
    'imap_port': 993,
    'imap_ssl': True,
    'imap_tls': False
}


def get_supported_server_info(mail_address: str, *allowed_protocols) -> dict:
    """Use user address to get server address and port.

    :param mail_address: str
    :return: ('protocol_server_address', port, ssl, tls)
    """
    provider = mail_address.split('@')[1]

    if provider in SUPPORTED_SERVER:
        return {k: v for k, v in SUPPORTED_SERVER[provider].items()
                if k.split('_')[0] in allowed_protocols}

    # Return default configs.
    return {(k + provider if 'host' in k else k): v
            for k, v in DEFAULT_SERVER_CONFIG.items()
            if k.split('_')[0] in allowed_protocols}


def get_enterprise_server_config(config: str) -> dict:
    """Get user-defined config.
    :param config: str
    :return: ('protocol_server_address', port, use_ssl)
    """
    if config in SUPPORTED_ENTERPRISE_SERVER_CONFIG:
        return SUPPORTED_ENTERPRISE_SERVER_CONFIG[config]
    return {}
