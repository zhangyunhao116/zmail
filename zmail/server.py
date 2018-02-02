"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import poplib
import logging

from email.mime.multipart import MIMEMultipart

from .utils import type_check, make_iterable
from .info import get_supported_server_info
from .settings import __level__, __status__

logger = logging.getLogger('zmail')


class MailServer:
    """This object communicate with server directly."""

    def __init__(self, user, password):
        type_check(str, user, password)

        self.user = user
        self.password = password

    def send_mail(self, recipients, message):
        """"Send email."""
        type_check(MIMEMultipart, message)

        self._message_add_from(message, self.user)

        recipients = make_iterable(recipients)

        host, port = get_supported_server_info(self.user, 'smtp')

        logger.info('Prepare login into {}:{}.'.format(host, port))
        with smtplib.SMTP_SSL(host, port) as server:
            if __status__ == 'dev':
                server.set_debuglevel(__level__)
            server.login(self.user, self.password)
            for recipient in recipients:
                self._message_add_to(message, recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def get_mail(self):
        """Get mail.using POP3 protocol."""
        host, port = get_supported_server_info(self.user, 'pop3')

        server = poplib.POP3_SSL(host, port)

        if __status__ == 'dev':
            server.set_debuglevel(__level__)

        logger.info('Prepare login into {}:{}.'.format(host, port))
        server.user(self.user)
        server.pass_(self.password)

        print(server.retr(4))

    @staticmethod
    def _message_add_from(message, sender_address):
        """Add 'From' header automatically to avoid server reject the mail."""
        if message['From'] is None:
            message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)

    @staticmethod
    def _message_add_to(message, recipient_address):
        """Add 'To' header automatically to avoid server reject the mail."""
        if message['To'] is None:
            message['To'] = '{}<{}>'.format(recipient_address.split('@')[0], recipient_address)
