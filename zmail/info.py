"""
zmail.info
~~~~~~~~~~~~
This module provide supported server information.


'Server_provider_address':{
    'protocol':('protocol_server_address', ssl_port,none_ssl_port),
}
"""
supported_server = {
    '163.com': {
        'smtp': ('smtp.163.com', 994, 25),
        'pop3': ('pop.163.com', 995, 110),
        'imap': ('imap.163.com', 993, 143)

    },
    '126.com': {
        'smtp': ('smtp.126.com', 994, 25),
        'pop3': ('pop.126.com', 995, 110),
        'imap': ('imap.126.com', 993, 143)

    },
    'yeah.net': {
        'smtp': ('smtp.yeah.net', 994, 25),
        'pop3': ('pop.yeah.net', 995, 110),
        'imap': ('imap.yeah.net', 993, 143)

    },
    'qq.com': {
        'smtp': ('smtp.qq.com', 25),
        'pop3': ('pop.qq.com', 995),
    },
    'gmail.com': {
        'smtp': ('smtp.gmail.com', 465, 443),
        'pop3': ('pop.gmail.com', 995),
    },
    'sina.com': {
        'smtp': ('smtp.sina.com', 465),
        'pop3': ('pop.sina.com', 995),
    },
}


def get_supported_server_info(mail_address, protocol, ssl=True):
    """Use user address to get server address and port."""
    provider = mail_address.split('@')[1]

    if provider in supported_server:
        server_info = supported_server[provider]
        if protocol in server_info:
            protocol_info = server_info[protocol]
            if ssl:
                return protocol_info[0], protocol_info[1]
            return protocol_info[0], protocol_info[2]
    else:
        if protocol == 'smtp' and ssl:
            return 'smtp.' + provider, 465
        elif protocol == 'pop3' and ssl:
            return 'pop.' + provider, 995

        raise Exception('{} is not supported now,or get a wrong mail address.'.format(mail_address))
