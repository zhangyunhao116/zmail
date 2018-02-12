"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import poplib
import logging

from .utils import make_iterable
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

        logger.info('Prepare login into {}:{}.'.format(host, port))
        server.user(self.user)
        server.pass_(self.password)


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


def _message_add_from(message, sender_address):
    """Add 'From' header to avoid server reject the mail."""
    message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)


def _message_add_to(message, recipient_address):
    """Add 'To' header to avoid server reject the mail."""
    message['To'] = '{}<{}>'.format(recipient_address.split('@')[0], recipient_address)
