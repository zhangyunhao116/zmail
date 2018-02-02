"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import logging

from email.mime.multipart import MIMEMultipart
from .utils import type_check, make_iterable
from .info import get_supported_server_info

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

        self._message_header_fix(message, self.user)

        recipients = make_iterable(recipients)

        host, port = get_supported_server_info(self.user, 'smtp')

        logger.info('Login into server %s:%s', host, port)
        with smtplib.SMTP_SSL(host, port) as server:
            server.set_debuglevel(logger.level)
            server.login(self.user, self.password)
            for recipient in recipients:
                server.sendmail(self.user, recipient, message.as_string())

    @staticmethod
    def _message_header_fix(message, sender_address):
        """Add 'From' header automatically to avoid server reject the mail."""
        if message['From'] is None:
            message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)
