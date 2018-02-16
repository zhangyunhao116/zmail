"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import poplib
import logging

from .utils import make_iterable
from .message import parse_header, mail_encode, mail_decode
from .info import get_supported_server_info
from .settings import __level__, __status__, __local__

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

        message = mail_encode(message)

        if ssl:
            server.send_ssl(recipients, message, timeout)
        else:
            server.send(recipients, message, timeout)

    def stat(self):
        """Get mailbox status."""
        server = self._init_pop3()
        status = server.stat()
        server.logout()

        return status

    def get_mail(self, which):
        """Get a mail from mailbox."""
        server = self._init_pop3()

        header, body = server.get_mail(which)

        server.logout()

        return mail_decode(header, body, which)

    def get_latest(self):
        """Get latest mail in mailbox."""
        server = self._init_pop3()

        latest_num = server.stat()[0]
        header, body = server.get_mail(latest_num)

        server.logout()

        return mail_decode(header, body, latest_num)

    def get_info(self):
        """Get all mails information.include(subject,from,to,date)"""
        server = self._init_pop3()

        result = server.get_info()

        server.logout()

        return result

    def _init_pop3(self):
        """Initiate POP3 server."""
        host, port, ssl = get_supported_server_info(self.user, 'pop3')
        logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))
        server = POP3Server(host, port, self.user, self.password, ssl)

        return server


class SMTPServer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_ssl(self, recipients, message, timeout):
        with smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=timeout) as server:
            if __status__ == 'dev_a':
                server.set_debuglevel(__level__)
            server.login(self.user, self.password)
            for recipient in recipients:
                _message_add_to(message, recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def send(self, recipients, message, timeout, tls=True):
        with smtplib.SMTP(self.host, self.port, __local__, timeout=timeout) as server:
            if __status__ == 'dev_a':
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
    def __init__(self, host, port, user, password, ssl=True, tls=True):
        self.user = user
        self.password = password

        self.pop3 = poplib.POP3_SSL(host, port) if ssl else poplib.POP3(host, port)

        if __status__ == 'dev_a':
            self.pop3.set_debuglevel(__level__)

        if tls and ssl is False:
            self.pop3.stls()
        self.login()

    def get_info(self):
        """Get all mails info. The result is the form [header_as_dict,...,] """
        num = self.stat()[0]
        result = []
        for count in range(1, num + 1):
            header = self.get_header(count)
            header_as_dict = parse_header(header)
            # Add mail id.
            header_as_dict['id'] = count
            result.append(header_as_dict)
        return result

    def login(self):
        self.pop3.user(self.user)
        self.pop3.pass_(self.password)

    def logout(self):
        self.pop3.quit()

    def stat(self):
        """Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size)."""
        return self.pop3.stat()

    def get_mail(self, which):
        """Get a mail by its id.
        ：:return (header,body)
        """
        header = self.pop3.top(which, 0)[1]

        body = self.pop3.retr(which)[1][len(header):]

        return header, body

    def get_header(self, which):
        """Use 'top' to get mail headers."""
        return self.pop3.top(which, 0)[1]


def _message_add_from(message, sender_address):
    """Add 'From' header to avoid server reject the mail."""
    message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)


def _message_add_to(message, recipient_address):
    """Add 'To' header to avoid server reject the mail."""
    message['To'] = '{}<{}>'.format(recipient_address.split('@')[0], recipient_address)
