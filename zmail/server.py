"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import smtplib
import poplib
import logging

from zmail.exceptions import InvalidProtocol
from zmail.info import get_supported_server_info
from zmail.message import mail_decode, Mail, decode_headers
from zmail.settings import __local__

# Fix poplib bug.
poplib._MAXLINE = 4096

logger = logging.getLogger('zmail')


class MailServer:
    """High-level MailServer API includes SMTPServer and POPServer."""

    def __init__(self, user: str, password: str, smtp_host: str, smtp_port: int, pop_host: str, pop_port: int,
                 smtp_ssl: bool, pop_ssl: bool, smtp_tls: bool, pop_tls: bool, timeout=60,
                 auto_add_from=True, auto_add_to=True):
        self.user = user
        self.password = password
        self.timeout = timeout

        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_ssl = smtp_ssl
        self.smtp_tls = smtp_tls

        self.pop_host = pop_host
        self.pop_port = pop_port
        self.pop_ssl = pop_ssl
        self.pop_tls = pop_tls

        self.auto_add_from = auto_add_from
        self.auto_add_to = auto_add_to

    def send_mail(self, recipients, message: dict, timeout=60) -> bool:
        """"Send email."""
        mail = Mail(message)

        if self.auto_add_from and mail.get('from') is None:
            mail['from'] = '{}<{}>'.format(self.user.split("@")[0], self.user)

        recipients = recipients if isinstance(recipients, (list, tuple)) else (recipients,)

        host, port, ssl, tls = get_supported_server_info(self.user, 'smtp')
        host = self.smtp_host if self.smtp_host is not None else host
        port = self.smtp_port if self.smtp_port is not None else port
        ssl = self.smtp_ssl if self.smtp_ssl is not None else ssl
        tls = self.pop_tls if self.pop_tls is not None else tls

        logger.info('Prepare login into {}:{} ssl:{} tls:{}.'.format(host, port, ssl, tls))

        server = SMTPServer(host, port, self.user, self.password)

        if ssl:
            server.send_ssl(recipients, mail, timeout, self.auto_add_to)
        else:
            server.send(recipients, mail, timeout, self.auto_add_to, tls)

        return True

    def stat(self) -> tuple:
        """Get mailbox status."""
        server = self._init_pop3()
        status = server.stat()
        server.logout()

        return status

    def get_mail(self, which: int):
        """Get a mail from mailbox."""
        server = self._init_pop3()

        mail = server.get_mail(which)

        server.logout()

        return mail_decode(mail, which)

    def get_mails(self, subject=None, after=None, before=None, sender=None):
        """Get a list of mails from mailbox."""
        info = self.get_info()
        mail_id = []

        for index, mail in enumerate(info):
            if self._match(decode_headers(mail), subject, after, before, sender):
                mail_id.append(index + 1)

        server = self._init_pop3()

        mail_id.sort()
        mail_as_bytes_list = server.get_mails(mail_id)
        server.logout()

        return [mail_decode(mail_as_bytes, mail_id[index]) for index, mail_as_bytes in enumerate(mail_as_bytes_list)]

    def get_latest(self):
        """Get latest mail in mailbox."""
        server = self._init_pop3()

        latest_num = server.stat()[0]
        mail = server.get_mail(latest_num)

        server.logout()

        return mail_decode(mail, latest_num)

    def get_info(self) -> list:
        """Get all mails information.include(subject,from,to,date)"""
        server = self._init_pop3()

        result = server.get_headers()

        server.logout()

        return result

    def smtp_able(self):
        host, port, ssl, tls = get_supported_server_info(self.user, 'smtp')
        host = self.smtp_host if self.smtp_host is not None else host
        port = self.smtp_port if self.smtp_port is not None else port
        ssl = self.smtp_ssl if self.smtp_ssl is not None else ssl
        tls = self.pop_tls if self.pop_tls is not None else tls

        logger.info('Prepare login into {}:{} ssl:{} tls:{}.'.format(host, port, ssl, tls))

        server = SMTPServer(host, port, self.user, self.password)
        return server.login_able(ssl, tls, self.timeout)

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
        host, port, ssl, tls = get_supported_server_info(self.user, 'pop3')
        host = self.pop_host if self.pop_host is not None else host
        port = self.pop_port if self.pop_port is not None else port
        ssl = self.pop_ssl if self.pop_ssl is not None else ssl
        tls = self.pop_tls if self.pop_tls is not None else tls

        logger.info('Prepare login into {}:{} ssl:{}.'.format(host, port, ssl))
        server = POP3Server(host, port, self.user, self.password, ssl, tls, self.timeout)

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
    """Base SMTPServer, which encapsulates python3 standard library to a SMTPServer."""

    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def send_ssl(self, recipients, message, timeout, auto_add_to):
        with smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=timeout) as server:
            server.login(self.user, self.password)
            for recipient in recipients:
                if auto_add_to and message.get('to') is None:
                    message['To'] = '{}<{}>'.format(recipient.split("@")[0], recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def send(self, recipients, message, timeout, auto_add_to, tls=True):
        with smtplib.SMTP(self.host, self.port, __local__, timeout=timeout) as server:
            if tls:
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(self.user, self.password)
            for recipient in recipients:
                if auto_add_to and message.get('to') is None:
                    message['To'] = '{}<{}>'.format(recipient.split("@")[0], recipient)
                server.sendmail(self.user, recipient, message.as_string())

    def login_able(self, use_ssl, use_tls, timeout):
        try:
            if use_ssl:
                with smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=timeout) as server:
                    server.login(self.user, self.password)
            else:
                with smtplib.SMTP(self.host, self.port, __local__, timeout=timeout) as server:
                    if use_tls:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                    server.login(self.user, self.password)
        except Exception as e:
            logger.warning('Login SMTP error :{}'.format(e))
            return False
        return True


class POP3Server:
    """Base POP3Server, which encapsulates python3 standard library to a SMTPServer."""

    def __init__(self, host: str, port: int, user: str, password: str, ssl=False, tls=False, timeout=60):
        self.user = user
        self.password = password

        self.pop3 = poplib.POP3_SSL(host, port, timeout=timeout) if ssl else poplib.POP3(host, port, timeout=timeout)

        if tls and not ssl:
            self.pop3.stls()
        elif tls and ssl:
            raise InvalidProtocol('Can not used ssl and tls together.')

        self.login()

    def login(self):
        """Note: the mailbox on the server is locked until logout() is called."""
        self.pop3.user(self.user)
        self.pop3.pass_(self.password)

    def logout(self):
        """Quit pop3 server."""
        self.pop3.quit()

    def stat(self) -> tuple:
        """Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size)."""
        return self.pop3.stat()

    def get_header(self, which) -> list:
        """Use 'top' to get mail headers."""
        return self.pop3.top(which, 0)[1]

    def get_headers(self) -> list:
        """Get all mails headers."""
        num = self.stat()[0]
        result = []
        for count in range(1, num + 1):
            header_as_bytes = self.get_header(count)
            result.append(header_as_bytes)
        return result

    def get_mail(self, which) -> list:
        """Get a mail by its id."""
        return self.pop3.retr(which)[1]

    def get_mails(self, which_list: list) -> list:
        """Get a list of mails by its id."""
        return [self.pop3.retr(which)[1] for which in which_list]
