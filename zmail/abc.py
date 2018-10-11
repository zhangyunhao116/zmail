import logging
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger('zmail')


class BaseServer(ABC):
    """Base protocol server."""

    def __init__(self, username: str, password: str,
                 host: str, port: int,
                 ssl: bool, tls: bool,
                 timeout: int or float,
                 debug: bool, log: Optional[logging.Logger] = None):
        self.server = None
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.timeout = timeout

        self.ssl = ssl
        self.tls = tls
        self.debug = debug
        self.log = log or logger

        self._login = False

        if tls and ssl:
            raise TypeError('Can not use ssl and tls together.')

    @abstractmethod
    def _make_server(self):
        pass

    def _remove_server(self):
        self.server = None

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def stls(self):
        pass

    def check_available(self) -> bool:
        try:
            self.login()
            self.logout()
            return True
        except Exception as e:
            self.log_exception('{} access error :{}'.format(self.__class__.__name__, e))
            return False

    def is_login(self) -> bool:
        return self._login

    def log_debug(self, msg):
        self.log.debug(msg)

    def log_exception(self, msg):
        self.log.fatal(msg)

    def log_access(self, msg):
        self.log_debug('<{} {}:{} ssl:{} tls:{} is_login:{}> {}.'
                       .format(self.__class__.__name__,
                               self.host, self.port,
                               self.ssl, self.tls,
                               self.is_login(), msg))

    def __enter__(self):
        self.login()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def __repr__(self):
        return '<{} username:{} password:{} ' \
               '{}:{} ssl:{} tls:{}>' \
            .format(self.__class__.__name__, self.username, self.password,
                    self.host, self.port, self.ssl, self.tls)
