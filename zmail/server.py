"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import poplib
import logging

from .utils import make_iterable
from .message import mail_encode, mail_decode, parse_header_shortcut
from .info import get_supported_server_info
from .settings import __level__, __local__, __protocol_log__

logger = logging.getLogger('zmail')

# Fix poplib bug.
poplib._MAXLINE = 4096


class MailServer:
    """This object communicate with server directly."""

    def __init__(self, user, password, smtp_host=None, smtp_port=None, pop_host=None, pop_port=None, smtp_ssl=None,
                 pop_ssl=None):
        self.user = user
        self.password = password

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_ssl = smtp_ssl

        self.pop_host = pop_host
        self.pop_port = pop_port
        self.pop_ssl = pop_ssl

    def send_mail(self, recipients, message, timeout=60):
        """"Send email."""

        _message_add_from(message, self.user)

        recipients = make_iterable(recipients)

        host, port, ssl = get_supported_server_info(self.user, 'smtp')
        host = self.smtp_host if self.smtp_host else host
        port = self.smtp_port if self.smtp_port else port
        ssl = self.pop_ssl if self.pop_ssl is not None else ssl

        logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))

        server = SMTPServer(host, port, self.user, self.password)

        message = mail_encode(message)

        if ssl:
            server.send_ssl(recipients, message, timeout)
        else:
            server.send(recipients, message, timeout)

        return True

    def stat(self):
        """Get mailbox status."""
        server = self._init_pop3()
        status = server.stat()
        server.logout()

        return status

    def get_mail(self, which):
        """Get a mail from mailbox."""
        server = self._init_pop3()

        mail = server.get_mail(which)

        server.logout()

        return mail_decode(mail, which)

    def get_mails(self, subject=None, after=None, before=None, sender=None):
        """Get a list of mails from mailbox."""
        info = self.get_info()
        mail_id = []
        result = []

        for mail in info:
            if self._match(mail, subject, after, before, sender):
                mail_id.append(int(mail['id']))

        server = self._init_pop3()

        for i in mail_id:
            mail = server.get_mail(i)
            result.append(mail_decode(mail, i))
        server.logout()

        return result

    def get_latest(self):
        """Get latest mail in mailbox."""
        server = self._init_pop3()

        latest_num = server.stat()[0]
        mail = server.get_mail(latest_num)

        server.logout()

        return mail_decode(mail, latest_num)

    def get_info(self):
        """Get all mails information.include(subject,from,to,date)"""
        server = self._init_pop3()

        result = server.get_info()

        server.logout()

        return result

    def smtp_able(self):
        try:
            host, port, ssl = get_supported_server_info(self.user, 'smtp')
            host = self.smtp_host if self.smtp_host else host
            port = self.smtp_port if self.smtp_port else port
            ssl = self.pop_ssl if self.pop_ssl is not None else ssl

            logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))

            server = SMTPServer(host, port, self.user, self.password)
            message = mail_encode({'subject': 'test', 'content': 'test'})

            if ssl:
                server.send_ssl([], message, 60)
            else:
                server.send([], message, 60)
            return True
        except Exception as e:
            logger.warning('Login smtp error :{}'.format(e))
            return False

    def pop_able(self):
        try:
            server = self._init_pop3()
            server.logout()
            return True
        except Exception as e:
            logger.warning('Login pop3 error :{}'.format(e))
            return False

    def _init_pop3(self):
        """Initiate POP3 server."""
        host, port, ssl = get_supported_server_info(self.user, 'pop3')
        host = self.pop_host if self.pop_host else host
        port = self.pop_port if self.pop_port else port
        ssl = self.pop_ssl if self.pop_ssl is not None else ssl

        logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))
        server = POP3Server(host, port, self.user, self.password, ssl)

        return server

    @staticmethod
    def _match(mail, subject=None, after=None, before=None, sender=None):
        """Match all conditions."""
        _subject = mail.get('subject', 'None')
        _sender = mail.get('from', 'None')

        _date = mail['date'].split(' ')[0]
        _time = tuple(map(lambda x: int(x), _date.split('-')))

        if subject and _subject.find(subject) == -1:
            return False

        if sender and _sender.find(sender) == -1:
            return False

        if before:
            # bf_year, bf_month, bf_day.
            before_time = tuple(map(lambda x: int(x), before.split('-')))
            for i in range(0, 3):
                if before_time[i] < _time[i]:
                    return False
                elif before_time[i] > _time[i]:
                    break
        if after:
            after_time = tuple(map(lambda x: int(x), after.split('-')))
            for i in range(0, 3):
                if after_time[i] > _time[i]:
                    return False
                elif after_time[i] < _time[i]:
                    break
        return True


class SMTPServer:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_ssl(self, recipients, message, timeout):
        with smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=timeout) as server:
            if __protocol_log__:
                server.set_debuglevel(__level__)
            server.login(self.user, self.password)
            for recipient in recipients:
                _message_add_to(message, recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def send(self, recipients, message, timeout, tls=True):
        with smtplib.SMTP(self.host, self.port, __local__, timeout=timeout) as server:
            if __protocol_log__:
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

        if __protocol_log__:
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
            header_as_dict = parse_header_shortcut(header)
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
        """Get a mail by its id."""

        mail = self.pop3.retr(which)[1]

        return mail

    def get_header(self, which):
        """Use 'top' to get mail headers."""
        return self.pop3.top(which, 0)[1]


def _message_add_from(message, sender_address):
    """Add 'From' header to avoid server reject the mail."""
    message['From'] = '{}<{}>'.format(sender_address.split('@')[0], sender_address)


def _message_add_to(message, recipient_address):
    """Add 'To' header to avoid server reject the mail."""
    message['To'] = '{}<{}>'.format(recipient_address.split('@')[0], recipient_address)
