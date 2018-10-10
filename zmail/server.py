"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import logging
import poplib
import smtplib
from typing import List

from zmail.abc import ProtocolServer
from zmail.message import Mail, decode_headers, mail_decode
from zmail.settings import __local__

# Fix poplib bug.
poplib._MAXLINE = 4096

logger = logging.getLogger('zmail')


class MailServer:

    def __init__(self, username: str, password: str,
                 smtp_host: str, smtp_port: int,
                 pop_host: str, pop_port: int,
                 smtp_ssl: bool, pop_ssl: bool,
                 smtp_tls: bool, pop_tls: bool,
                 debug: bool, log=None, timeout=60,
                 auto_add_from=True, auto_add_to=True):
        self.username = username
        self.password = password
        self.debug = debug
        self.log = log or logger
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

        self.smtp_server = None  # type:SMTPServer
        self.pop_server = None  # type:POPServer

        self.prepare()

    def prepare(self):
        """Init SMTPServer and POPServer."""
        if self.smtp_server is None:
            self.smtp_server = SMTPServer(self.username, self.password,
                                          self.smtp_host, self.smtp_port,
                                          self.timeout, self.smtp_ssl, self.smtp_tls,
                                          self.debug, self.log)
        if self.pop_server is None:
            self.pop_server = POPServer(self.username, self.password,
                                        self.pop_host, self.pop_port,
                                        self.timeout, self.pop_ssl, self.pop_tls,
                                        self.debug, self.log)

    def send_mail(self, recipients: List[str], message: dict, timeout=None,
                  auto_add_from=None, auto_add_to=None) -> bool:
        """"Send email."""
        mail = Mail(message)

        if (auto_add_from or self.auto_add_from) and mail.get('from') is None:
            mail['from'] = '{}<{}>'.format(self.username.split("@")[0], self.username)

        recipients = recipients if isinstance(recipients, (list, tuple)) else (recipients,)

        with self.smtp_server as server:
            server.send(recipients, mail, timeout or self.timeout, auto_add_to or self.auto_add_to)

        return True

    def stat(self) -> tuple:
        """Get mailbox status."""
        with self.pop_server as server:
            return server.stat()

    def get_mail(self, which: int):
        """Get a mail from mailbox."""
        with self.pop_server as server:
            mail = server.get_mail(which)
            return mail_decode(mail, which)

    def get_mails(self, subject=None, after=None, before=None, sender=None):
        """Get a list of mails from mailbox."""
        info = self.get_info()
        mail_id = []

        for index, mail in enumerate(info):
            if self._match(decode_headers(mail), subject, after, before, sender):
                mail_id.append(index + 1)

        with self.pop_server as server:
            mail_id.sort()
            mail_as_bytes_list = server.get_mails(mail_id)
            return [mail_decode(mail_as_bytes, mail_id[index])
                    for index, mail_as_bytes in enumerate(mail_as_bytes_list)]

    def get_latest(self):
        """Get latest mail in mailbox."""
        with self.pop_server as server:
            latest_num = server.stat()[0]
            mail = server.get_mail(latest_num)
            return mail_decode(mail, latest_num)

    def get_info(self) -> list:
        """Get all mails information.include(subject,from,to,date)"""
        with self.pop_server as server:
            return server.get_headers()

    def log_debug(self, *args, **kwargs):
        self.log.debug(*args, **kwargs)

    def log_exception(self, *args, **kwargs):
        self.log_exception(*args, **kwargs)

    def smtp_able(self):
        return self.smtp_server.check_available()

    def pop_able(self):
        return self.pop_server.check_available()

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


class SMTPServer(ProtocolServer):
    """Base SMTPServer, which encapsulates python3 standard library to a SMTPServer."""

    def _make_server(self):
        """Init Server."""
        if self.server is None:
            if self.ssl:
                self.server = smtplib.SMTP_SSL(self.host, self.port, __local__, timeout=self.timeout)
            else:
                self.server = smtplib.SMTP(self.host, self.port, __local__, timeout=self.timeout)

    def _remove_server(self):
        self.server = None

    def login(self):
        if self._login:
            self.log_exception('{} duplicate login!'.format(self.__repr__()))
            return

        if self.debug:
            self.log_access('login')

        self._make_server()

        if self.tls:
            self.stls()

        self.server.login(self.username, self.password)

        self._login = True

    def logout(self):
        if not self._login:
            self.log_exception('{} Logout before login!'.format(self.__repr__()))
            return

        if self.debug:
            self.log_access('logout')

        # Copied from smtplib.SMTP.__exit__
        # used for close connection.
        try:
            code, message = self.server.docmd("QUIT")
            if code != 221:
                raise smtplib.SMTPResponseException(code, message)
        except smtplib.SMTPServerDisconnected:
            pass
        finally:
            self.server.close()

        self._remove_server()

        self._login = False

    def stls(self):
        """Start TLS."""
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()

    # Methods
    def send(self, recipients: List[str], message,
             timeout: int or float or None, auto_add_to: bool):

        if timeout is not None:
            self.server.timeout = timeout

        for recipient in recipients:
            if auto_add_to and message.get('to') is None:
                message['To'] = '{}<{}>'.format(recipient.split("@")[0], recipient)
            self.server.sendmail(self.username, recipient, message.as_string())


class POPServer(ProtocolServer):
    """Base POPServer, which encapsulates python3 standard library to a POPServer."""

    def _make_server(self):
        """Init Server."""
        if self.server is None:
            if self.ssl:
                self.server = poplib.POP3_SSL(self.host, self.port, timeout=self.timeout)
            else:
                self.server = poplib.POP3(self.host, self.port, timeout=self.timeout)

    def _remove_server(self):
        self.server = None

    def login(self):
        """Note: the mailbox on the server is locked until logout() is called."""
        if self._login:
            self.log_exception('{} duplicate login!'.format(self.__repr__()))
            return

        if self.debug:
            self.log_access('login')

        self._make_server()

        if self.tls:
            self.stls()

        self.server.user(self.username)
        self.server.pass_(self.password)

        self._login = True

    def logout(self):
        """Quit and remove pop3 server."""
        if not self._login:
            self.log_exception('{} Logout before login!'.format(self.__repr__()))
            return

        if self.debug:
            self.log_access('logout')

        self.server.quit()

        self._remove_server()

        self._login = False

    def stls(self):
        self.server.stls()

    # Methods

    def stat(self) -> tuple:
        """Get mailbox status. The result is a tuple of 2 integers: (message count, mailbox size)."""
        return self.server.stat()

    def get_header(self, which: int) -> list:
        """Use 'top' to get mail headers."""
        return self.server.top(which, 0)[1]

    def get_headers(self) -> list:
        """Get all mails headers."""
        num = self.stat()[0]
        result = []
        for count in range(1, num + 1):
            header_as_bytes = self.get_header(count)
            result.append(header_as_bytes)
        return result

    def get_mail(self, which: int) -> list:
        """Get a mail by its id."""
        return self.server.retr(which)[1]

    def get_mails(self, which_list: list) -> list:
        """Get a list of mails by its id."""
        return [self.server.retr(which)[1] for which in which_list]
