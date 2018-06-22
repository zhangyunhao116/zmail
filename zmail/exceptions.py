class ZmailException(IOError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class InvalidProtocol(ZmailException, ValueError):
    """Invalid protocol settings used."""
