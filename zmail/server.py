"""
zmail.server
~~~~~~~~~~~~
This module provides a MailServer object to communicate with mail server.
"""

import datetime
import logging
import poplib
import smtplib
import warnings
from typing import Iterable, List, Optional

from .abc import BaseServer
from .exceptions import InvalidArguments
from .helpers import (convert_date_to_datetime, first_not_none,
                      get_intersection, make_address_header, make_list,
                      match_conditions)
from .mime import Mail
from .parser import parse_headers, parse_mail
from .settings import __local__
from .structures import CaseInsensitiveDict

# Fix poplib bug.
poplib._MAXLINE = 4096

logger = logging.getLogger('zmail')


class MailServer:

    def __init__(self, username: str, password: str,
                 smtp_host: str, smtp_port: int,
                 pop_host: str, pop_port: int,
                 smtp_ssl: bool, pop_ssl: bool,
                 smtp_tls: bool, pop_tls: bool,
                 debug: bool = False, log=None, timeout=60,
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

        self.smtp_server = None  # type:SMTPServer or None
        self.pop_server = None  # type:POPServer or None

        # Check arguments.
        if not isinstance(self.log, logging.Logger):
            raise InvalidArguments('log excepted type logging.Logger got {}'.format(type(self.log)))

        if not isinstance(self.timeout, (int, float)):
            raise InvalidArguments('timeout excepted type int or float got {}'.format(type(self.timeout)))

        self.prepare()

    def prepare(self):
        """Init SMTPServer and POPServer."""
        if self.smtp_server is None:
            self.smtp_server = SMTPServer(username=self.username,
                                          password=self.password,
                                          host=self.smtp_host,
                                          port=self.smtp_port,
                                          ssl=self.smtp_ssl,
                                          tls=self.smtp_tls,
                                          timeout=self.timeout,
                                          debug=self.debug,
                                          log=self.log)
        if self.pop_server is None:
            self.pop_server = POPServer(username=self.username,
                                        password=self.password,
                                        host=self.pop_host,
                                        port=self.pop_port,
                                        ssl=self.pop_ssl,
                                        tls=self.pop_tls,
                                        timeout=self.timeout,
                                        debug=self.debug,
                                        log=self.log)

    def send_mail(self, recipients: List[str] or str, mail: dict or CaseInsensitiveDict, cc=None,
                  timeout=None, auto_add_from=True, auto_add_to=True) -> bool:
        """"Send email."""
        _mail = Mail(mail, debug=self.debug, log=self.log)

        if first_not_none(auto_add_from, self.auto_add_from) and _mail.mail.get('From') is None:
            _mail.set_mime_header('From', make_address_header([self.username]))

        recipients = make_list(recipients)
        if first_not_none(auto_add_to, self.auto_add_to) and _mail.mail.get('To') is None:
            _mail.set_mime_header('To', make_address_header(recipients))

        # Add Carbon Copy address.
        cc = make_list(cc) if cc is not None else None
        if cc is not None:
            for address in cc:
                recipients.append(address)
            _mail.set_mime_header('Cc', make_address_header(cc))

        # Remove tuple format in recipients.
        recipients = [i if not isinstance(i, tuple) else i[1] for i in recipients]

        with self.smtp_server as server:
            server.send(recipients, _mail,
                        first_not_none(timeout, self.timeout))

        return True

    def delete(self, which: int) -> bool:
        """Delete mail."""
        with self.pop_server as server:
            server.delete(which)
        return True

    def stat(self) -> tuple:
        """Get mailbox status."""
        with self.pop_server as server:
            return server.stat()

    def get_mail(self, which: int) -> CaseInsensitiveDict:
        """Get a mail from mailbox."""
        with self.pop_server as server:
            mail = server.get_mail(which)
            return parse_mail(mail, which, self.debug, self.log)

    def get_mails(self, subject=None, start_time=None, end_time=None, sender=None,
                  start_index: Optional[int] = None, end_index: Optional[int] = None) -> list:
        """Get a list of mails from mailbox."""
        headers = self.get_headers(start_index, end_index)
        mail_id = []

        if start_time is not None:
            if isinstance(start_time, (datetime.datetime, str)):
                start_time = convert_date_to_datetime(start_time)
            else:
                raise InvalidArguments(
                    'start_time excepted type str or datetime.datetime, got {} instead.'.format(type(start_time)))

        if end_time is not None:
            if isinstance(end_time, (datetime.datetime, str)):
                end_time = convert_date_to_datetime(end_time)
            else:
                raise InvalidArguments(
                    'end_time excepted type str or datetime.datetime, got {} instead.'.format(type(end_time)))

        for header in headers:
            if match_conditions(header, subject, start_time, end_time, sender):
                mail_id.append(header['id'])

        with self.pop_server as server:
            mail_id.sort()
            mail_as_bytes_list = server.get_mails(mail_id)
            return [parse_mail(mail_as_bytes, mail_id[index], self.debug, self.log)
                    for index, mail_as_bytes in enumerate(mail_as_bytes_list)]

    def get_latest(self) -> CaseInsensitiveDict:
        """Get latest mail in mailbox."""
        with self.pop_server as server:
            latest_num = server.stat()[0]
            mail = server.get_mail(latest_num)
            return parse_mail(mail, latest_num, self.debug, self.log)

    def get_info(self) -> List[List[bytes]]:
        warnings.warn("server.get_info is deprecated, if you want to access mail headers,"
                      "use server.get_headers instead",
                      DeprecationWarning,
                      stacklevel=2)
        with self.pop_server as server:
            return server.get_headers()

    def get_headers(self, start_index: Optional[int] = None, end_index: Optional[int] = None) \
            -> List[CaseInsensitiveDict]:
        """Get mails headers."""
        headers = []

        with self.pop_server as server:
            end = server.stat()[0]
            intersection = get_intersection((1, end), (start_index, end_index))  # type:List[int]
            mail_hdrs = server.get_headers(intersection)

        for index, mail_header in enumerate(mail_hdrs):
            _, _headers, *__ = parse_headers(mail_header)
            _headers.update(id=intersection[index])
            headers.append(_headers)

        return headers

    def log_debug(self, *args, **kwargs):
        self.log.debug(*args, **kwargs)

    def log_exception(self, *args, **kwargs):
        self.log_exception(*args, **kwargs)

    def smtp_able(self) -> bool:
        return self.smtp_server.check_available()

    def pop_able(self) -> bool:
        return self.pop_server.check_available()


class SMTPServer(BaseServer):
    """Base SMTPServer, which encapsulates python3 standard library to a SMTPServer."""

    def _make_server(self):
        """Init Server if possible."""
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
    def send(self, recipients: Iterable[str], mail: Mail,
             timeout: int or float or None):

        if timeout is not None:
            self.server.timeout = timeout

        self.server.sendmail(self.username, recipients, mail.get_mime_as_string())


class POPServer(BaseServer):
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

    def get_headers(self, which_list: Optional[list] = None) -> list:
        """Get all mails headers."""
        num = self.stat()[0]
        result = []

        if which_list is None:
            _range = range(1, num + 1)
        else:
            _range = which_list

        for count in _range:
            header_as_bytes = self.get_header(count)
            result.append(header_as_bytes)

        return result

    def get_mail(self, which: int) -> list:
        """Get a mail by its id."""
        return self.server.retr(which)[1]

    def get_mails(self, which_list: list) -> list:
        """Get a list of mails by its id."""
        return [self.server.retr(which)[1] for which in which_list]

    def delete(self, which: int):
        self.server.dele(which)
