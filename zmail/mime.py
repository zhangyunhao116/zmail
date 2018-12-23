import logging
import os
import warnings
from email.encoders import encode_base64
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from .exceptions import InvalidArguments
from .helpers import get_abs_path, make_list
from .parser import parse
from .structures import CaseInsensitiveDict

logger = logging.getLogger('zmail')


class Mail:
    def __init__(self, mail: dict or CaseInsensitiveDict, boundary: Optional[str] = None,
                 debug: bool = False, log: logging.Logger = None):
        if isinstance(mail, dict):
            self.mail = CaseInsensitiveDict(mail)
        elif isinstance(mail, CaseInsensitiveDict):
            self.mail = mail
        else:
            raise InvalidArguments('mail field excepted type dict or CaseInsensitiveDict got {}'.format(type(mail)))

        self.boundary = boundary
        self.debug = debug
        self.log = log or logger
        self.mime = None  # type:MIMEMultipart

    def make_mine(self) -> None:
        mime = MIMEMultipart(boundary=self.boundary)

        # Set basic email elements.
        for k, v in self.mail.items():
            _k = k.lower()
            if _k in ('subject', 'from'):
                if isinstance(v, str):
                    mime[_k.capitalize()] = v
                else:
                    raise InvalidArguments('{} can only be str! Got {} instead.'.format(_k.capitalize(), type(v)))
            elif _k == 'to':
                if not self._is_resend_mail():
                    warnings.warn("Header 'to' is invalid and unused,if you want to add address name "
                                  "use tuple (address,name) instead.", category=DeprecationWarning, stacklevel=4)
            elif _k in ('attachments', 'content_text', 'content_html', 'headers'):
                pass
            else:
                if not self._is_resend_mail():
                    # Remove resend warnings.
                    warnings.warn("Header '{}' is invalid and unused,if you want to add extra headers "
                                  "use 'headers' instead.".format(str(_k)), category=DeprecationWarning, stacklevel=4)

        # Set extra headers.
        if self.mail.get('headers') and isinstance(self.mail['headers'], dict):
            for k, v in self.mail['headers'].items():
                mime[k] = v

        # Set HTML content.
        if self.mail.get('content_html') is not None:
            _htmls = make_list(self.mail['content_html'])
            for _html in _htmls:
                mime.attach(MIMEText('{}'.format(_html), 'html', 'utf-8'))

        # Set TEXT content.
        if self.mail.get('content_text') is not None:
            _messages = make_list(self.mail['content_text'])
            for _message in _messages:
                mime.attach(MIMEText('{}'.format(_message), 'plain', 'utf-8'))

        # Set attachments.
        if self.mail.get('attachments'):
            attachments = make_list(self.mail['attachments'])
            for attachment in attachments:
                if isinstance(attachment, str):
                    attachment_abs_path = get_abs_path(attachment)
                    part = make_attachment_part(attachment_abs_path)
                    mime.attach(part)
                elif isinstance(attachment, tuple):
                    name, raw = attachment
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(raw)
                    part['Content-Disposition'] = 'attachment;filename="{}"'.format(name)
                    encode_base64(part)
                    mime.attach(part)
                else:
                    raise InvalidArguments('Attachments excepted str or tuple got {} instead.'.format(type(attachment)))

        self.mime = mime

    def set_mime_header(self, k, v) -> None:
        if self.mime is not None:
            self.mime[k] = v
        else:
            self.make_mine()
            self.mime[k] = v

    def decode(self) -> CaseInsensitiveDict:
        if self.mime is None:
            self.make_mine()
        return parse(self.mime.as_string().encode('utf-8').split(b'\n'))

    def get_mime_raw(self) -> MIMEMultipart:
        if self.mime is not None:
            return self.mime
        else:
            self.make_mine()
            return self.mime

    def get_mime_as_string(self) -> str:
        return self.get_mime_raw().as_string()

    def get_mime_as_bytes_list(self) -> List[bytes]:
        return self.get_mime_as_string().encode('utf-8').split(b'\n')

    def _is_resend_mail(self) -> bool:
        return all([(i in self.mail) for i in
                    ('from', 'to', 'subject', 'raw_headers', 'charsets', 'headers',
                     'date', 'id', 'raw', 'attachments', 'content_text', 'content_html')])


def make_attachment_part(file_path) -> MIMEBase:
    """According to file-type return a prepared attachment part."""
    name = os.path.split(file_path)[1]
    encoded_name = Header(name).encode()

    file_type = 'application/octet-stream'
    main_type, sub_type = file_type.split('/')

    with open(file_path, 'rb') as f:
        part = MIMEBase(main_type, sub_type)
        part.set_payload(f.read())
        part['Content-Disposition'] = 'attachment;filename="{}"'.format(encoded_name)
        encode_base64(part)
    return part
