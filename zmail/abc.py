import logging
from abc import ABC, abstractmethod

logger = logging.getLogger('zmail')


class ProtocolServer(ABC):
    """Base protocol server."""

    def __init__(self, username: str, password: str,
                 host: str, port: int, timeout: int or float,
                 ssl: bool, tls: bool,
                 debug: bool, log=None):
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
    def login(self):
        pass

    @abstractmethod
    def logout(self):
        pass

    @abstractmethod
    def check_available(self) -> bool:
        pass

    def is_login(self) -> bool:
        return self._login

    def log_debug(self, msg):
        self.log.debug(msg)

    def log_exception(self, msg):
        self.log.fatal(msg)

    def __repr__(self):
        return '<{} username:{} password:{} ' \
               '{}:{} ssl:{} tls:{}>' \
            .format(self.__class__.__name__, self.username, self.password,
                    self.host, self.port, self.ssl, self.tls)
