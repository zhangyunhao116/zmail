"""
zmail.info
~~~~~~~~~~~~
This module provide supported server information.


'Server_provider_address':{
    'protocol':('protocol_server_address', port, ssl),
}
"""
supported_server = {
    '163.com': {
        'smtp': ('smtp.163.com', 994, True),
        'pop3': ('pop.163.com', 995, True),
        'imap': ('imap.163.com', 993, True)

    },
    '126.com': {
        'smtp': ('smtp.126.com', 994, True),
        'pop3': ('pop.126.com', 995, True),
        'imap': ('imap.126.com', 993, True)

    },
    'yeah.net': {
        'smtp': ('smtp.yeah.net', 994, True),
        'pop3': ('pop.yeah.net', 995, True),
        'imap': ('imap.yeah.net', 993, True)

    },
    'qq.com': {
        'smtp': ('smtp.qq.com', 465, True),
        'pop3': ('pop.qq.com', 995, True),
    },
    'gmail.com': {
        'smtp': ('smtp.gmail.com', 587, False),
        'pop3': ('pop.gmail.com', 995, True),
    },
    'sina.com': {
        'smtp': ('smtp.sina.com', 465, True),
        'pop3': ('pop.sina.com', 995, True),
    },
    'outlook.com': {
        'smtp': ('smtp-mail.outlook.com', 587, False),
        'pop3': ('pop.outlook.com', 995, True),
    },

}
supported_server_config = {
    'qqexmail': {
        'smtp_host': 'smtp.exmail.qq.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'pop_host': 'pop.exmail.qq.com',
        'pop_port': 995,
        'pop_ssl': True,
    },
    'aliyunexmail': {
        'smtp_host': 'smtp.mxhichina.com',
        'smtp_port': 465,
        'smtp_ssl': True,
        'pop_host': 'pop3.mxhichina.com',
        'pop_port': 995,
        'pop_ssl': True,
    },

}


def get_supported_server_info(mail_address, protocol):
    """Use user address to get server address and port."""
    provider = mail_address.split('@')[1]

    if provider in supported_server:
        server_info = supported_server[provider]
        if protocol in server_info:
            return server_info[protocol]

    if protocol == 'smtp':
        return 'smtp.' + provider, 465, True
    elif protocol == 'pop3':
        return 'pop3.' + provider, 995, True


def get_server_config(config):
    """Get user-defined config."""
    if config in supported_server_config:
        return supported_server_config[config]
    else:
        return False
