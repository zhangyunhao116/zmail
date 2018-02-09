"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import re
import smtplib
import poplib
import logging

from .utils import make_iterable
from .info import get_supported_server_info, __month__
from .settings import __level__, __status__, __local__

from base64 import b64decode
from email.header import decode_header
from email.parser import BytesParser

logger = logging.getLogger('zmail')


class MailServer:
    """This object communicate with server directly."""

    def __init__(self, user, password):
        self.user = user
        self.password = password

    def send_mail(self, recipients, message, timeout=60):
        """"Send email."""

        _message_add_from(message, self.user)

        recipients = make_iterable(recipients)

        host, port, ssl = get_supported_server_info(self.user, 'smtp')

        logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))

        server = SMTPServer(host, port, self.user, self.password)

        if ssl:
            server.send_ssl(recipients, message, timeout)
        else:
            server.send(recipients, message, timeout)

    def get_mail(self):
        """Get mail.using POP3 protocol."""
        host, port, ssl = get_supported_server_info(self.user, 'pop3')

        server = poplib.POP3_SSL(host, port)

        if __status__ == 'dev':
            server.set_debuglevel(__level__)

        a = POP3Server(host, port, self.user, self.password, ssl)
        a.info()
        a.logout()

    def get_all_info(self):
        """Get all mails information.include(subject,)"""
        host, port, ssl = get_supported_server_info(self.user, 'pop3')

        server = poplib.POP3_SSL(host, port)

        if __status__ == 'dev':
            server.set_debuglevel(__level__)

        a = POP3Server(host, port, self.user, self.password, ssl)
        a.info()
        a.logout()


class SMTPServer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_ssl(self, recipients, message, timeout):
        with smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=timeout) as server:
            if __status__ == 'dev':
                server.set_debuglevel(__level__)
            server.login(self.user, self.password)
            for recipient in recipients:
                _message_add_to(message, recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def send(self, recipients, message, timeout, tls=True):
        with smtplib.SMTP(self.host, self.port, __local__, timeout=timeout) as server:
            if __status__ == 'dev':
                server.set_debuglevel(__level__)
            if tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(self.user, self.password)
            for recipient in recipients:
                _message_add_to(message, recipient)
                server.sendmail(self.user, recipient, message.as_string())


class POP3Server:
    def __init__(self, host, port, user, password, ssl=True):
        self.user = user
        self.password = password

        self.pop3 = poplib.POP3_SSL(host, port) if ssl else poplib.POP3(host, port)

        if __status__ == 'dev':
            self.pop3.set_debuglevel(__level__)

        self.login()

    def login(self):
        self.pop3.user(self.user)
        self.pop3.pass_(self.password)

    def info(self):
        """Get mail info. The result is the form [(mail_id, mail_size, mail_digest)] """
        num = self.stat()[0]
        for i in range(1, num):
            a = self._get_header(i)
            r = parse_header(a)
            for k in r:
                print(k, r[k])

    def logout(self):
        self.pop3.quit()

    def stat(self):
        """Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size)."""
        return self.pop3.stat()

    def _get_header(self, which):
        """Use 'top' to get mail headers."""
        return self.pop3.top(which, 0)[1]


def parse_header(_bytes_header):
    """Parse mail header then return a dictionary include basic elements in email."""
    _headers = ('From', 'To', 'Date', 'Subject')
    _string_header = _bytes_list_decode(_bytes_header)
    headers = []
    result = {}
    for i in _string_header:
        for header in _headers:
            if re.match(header, i):
                # Get basic mail headers.
                part = ''
                for section in decode_header(i):
                    if section[1] is None and isinstance(section[0], str):
                        part = part + section[0]
                    elif section[1] is None:
                        part = part + section[0].decode()
                    else:
                        part = part + section[0].decode(section[1])
                headers.append(part)

    # Convert headers list to a dictionary object.
    for j in headers:
        header_split = j.split(' ')
        if len(header_split) == 2:
            result[header_split[0][:-1].lower()] = header_split[1]
        elif header_split[0][:-1] == 'Date':
            result['date'] = header_split[1:]
        else:
            result[header_split[0][:-1].lower()] = ''.join(header_split[1:])

    result['date'] = _fmt_date(result['date'])

    return result


def _bytes_list_decode(bytes_list):
    """Decode a list of bytes-objects to a list of string-objects."""
    return tuple(map(lambda x: x.decode(), bytes_list))


def _fmt_date(date_list):
    """Format mail header Date for humans."""
    day = date_list[1]
    month = __month__[date_list[2]]
    year = date_list[3]
    times = date_list[4]
    time_zone = date_list[5]

    return '{}-{}-{} {} {}'.format(year, month, day, times, time_zone)


def _message_add_from(message, sender_address):
    """Add 'From' header to avoid server reject the mail."""
    message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)


def _message_add_to(message, recipient_address):
    """Add 'To' header to avoid server reject the mail."""
    message['To'] = '{}<{}>'.format(recipient_address.split('@')[0], recipient_address)
