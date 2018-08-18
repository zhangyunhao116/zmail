"""
zmail.message
~~~~~~~~~~~~
This module provides functions to handles MIME object.
"""
import os
import re
import quopri
import base64
import logging
import mimetypes
import collections

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.header import decode_header, Header

from .utils import get_abs_path, make_iterable
from .structures import CaseInsensitiveDict

logger = logging.getLogger('zmail')


class Mail(collections.MutableMapping):
    basic_item = ('subject', 'from', 'to', 'date', 'content-type')
    optional_item = ('content-transfer-encoding', 'boundary', 'charset',  # All three from parsed headers.
                     'id',  # From mail servers.
                     'raw',  # Raw data.
                     'headers',  # Parsed headers as dict.
                     'as_string',  # As string for send.
                     'content',  # From parsed body or user(for send).
                     'content-html',  # From parsed body or user(for send).
                     'attachments',  # From parsed body or user(for send).
                     )

    def __init__(self, data=None, **kwargs):
        self._store = {}
        self.mime = None
        self.as_bytes_list = None

        if data is None:
            self.update(**kwargs)
        elif isinstance(data, dict):
            self.update(data, **kwargs)
        elif isinstance(data, (list, tuple)):
            self.as_bytes_list = data

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        try:
            return self._store[key.lower()][1]
        except KeyError:
            if key.lower() in self.basic_item or key.lower() in self.optional_item:
                return None
            raise

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (raw_key for raw_key, _ in self._store.values())

    def __len__(self):
        return len(self._store)

    def __eq__(self, other):
        """Compared insensitively."""
        if isinstance(other, collections.Mapping):
            other = Mail(other)
        else:
            return NotImplemented
        return dict(self.lower_items()) == dict(other.lower_items())

    def lower_items(self):
        return (
            (lower_key, value[1])
            for (lower_key, value)
            in self._store.items()
        )

    def copy(self):
        """Shallow copy."""
        return Mail(self._store.values())

    def set_default_value(self, value=None):
        for i in self.basic_item:
            if i not in self._store:
                self[i] = value
        for i in self.optional_item:
            if i not in self._store:
                self[i] = value
        return self

    def pre_send(self):
        """Make a MIME obj for send."""
        logger.info('Making MIME obj.')

        mime = MIMEMultipart()
        # Set basic email elements.
        for k, v in self.lower_items():
            if k in ('from', 'to', 'subject') and v:
                mime[k.capitalize()] = v

        # Set extra parameters.
        for k in self:
            if k.lower() not in ('from', 'to', 'subject', 'attachments', 'content', 'content_html', 'content-html'):
                mime[k] = self[k]

        # Set mail content.
        if self.get('content_html'):
            mime.attach(MIMEText('%s' % self['content_html'], 'html', 'utf-8'))
        elif self.get('content-html'):
            mime.attach(MIMEText('%s' % self['content-html'], 'html', 'utf-8'))

        if self['content']:
            _message = make_iterable(self['content'])
            _combine_message = ''.join(_message)
            mime.attach(MIMEText('{}'.format(_combine_message), 'plain', 'utf-8'))

        # Set attachments.
        if self['attachments']:
            attachments = make_iterable(self['attachments'])
            for attachment in attachments:
                logger.info('Loading %s', attachment)
                attachment = get_abs_path(attachment)
                part = self._get_attachment_part(attachment)
                mime.attach(part)

        self.mime = mime

        return self

    def as_string(self):
        if self.mime is None:
            self.pre_send()
        elif isinstance(self.mime, MIMEMultipart):
            pass
        else:
            raise ValueError('MIME should be MIMEMultipart or None.')

        return self.mime.as_string()

    def as_bytes(self):
        if self.mime is None:
            self.pre_send()
        elif isinstance(self.mime, MIMEMultipart):
            pass
        else:
            raise ValueError('MIME should be MIMEMultipart or None.')

        return self.mime.as_bytes()

    def set_boundary(self, boundary):
        if self.mime is None:
            self.pre_send()
        elif isinstance(self.mime, MIMEMultipart):
            pass
        else:
            raise ValueError('MIME should be MIMEMultipart or None.')

        self.mime.set_boundary(boundary)

        return self

    def decode(self):
        if self.as_bytes_list is None:
            raise TypeError('Need mail as bytes list.')
        return MailDecode(self.as_bytes_list).get_decoded_result()

    @staticmethod
    def _get_attachment_part(file):
        """According to file-type return a prepared attachment part."""
        name = os.path.split(file)[1]
        file_type = mimetypes.guess_type(name)[0]

        encoded_name = Header(name).encode()

        if file_type is None:
            logger.warning('Could not guess %s type, use application type instead.', file)
            file_type = 'application/octet-stream'

        main_type, sub_type = file_type.split('/')

        if main_type == 'text':
            with open(file, 'r') as f:
                part = MIMEText(f.read())
                part['Content-Disposition'] = 'attachment;filename="%s"' % encoded_name

        elif main_type in ('image', 'audio'):
            with open(file, 'rb') as f:
                part = MIMEImage(f.read(), _subtype=sub_type) if main_type == 'image' else \
                    MIMEAudio(f.read(), _subtype=sub_type)
                part['Content-Disposition'] = 'attachment;filename="%s"' % encoded_name
        else:
            with open(file, 'rb') as f:
                part = MIMEBase(main_type, sub_type)
                part.set_payload(f.read())
                part['Content-Disposition'] = 'attachment;filename="%s"' % encoded_name
                encode_base64(part)

        return part

    def __repr__(self):
        return str(dict(self.items()))


def mail_decode(mail_as_bytes, which=-1):
    """Convert a MIME bytes to dict."""
    return MailDecode(mail_as_bytes, which).get_decoded_result()


def parse_header(mail_as_bytes, *args):
    """Parse mail header then return a dictionary include basic elements in email.

    :param mail_as_bytes: mail as bytes
    :param args: extra parameters

    :return: dict {'header_as_str':'value_as_bytes'}
    """
    email_headers = {}

    # Parse headers.
    extra_header = {}
    for i in args:
        extra_header[i] = None
    extra_pattern = rb"""[\s]?=["'\s]?([^"';\\\r\n\s]+)["';\r\n\s]?"""

    part = b''
    header = b''

    for line in mail_as_bytes:
        # Get extra_header if possible.
        for k, v in extra_header.items():
            if v is None and re.search(bytes(k, encoding='utf8') + bytes(extra_pattern), line):
                extra_header[k] = re.search(bytes(k, encoding='utf8') + bytes(extra_pattern), line).group(1)

        # Parsing header.
        if re.fullmatch(rb'([0-9a-zA-Z-]+):\s?([^\r\n]+)(\r\n)?', line):
            # Line is a header.
            if part and header:
                email_headers[header.decode()] = part
            header, part = re.search(rb'([0-9a-zA-Z-]+):\s?([^\r\n]+)(\r\n)?', line).group(1, 2)
        elif re.fullmatch(rb'[\t]?([^\r\n]+)(\r\n)?', line):
            # Line is a part of header.
            _part = re.search(rb'[\t]?([^\r\n]+)(\r\n)?', line).group(1)
            part += _part
        elif line in (b'\r\n', b''):
            # Mail header boundary.
            if part and header:
                email_headers[header.decode()] = part
            break
        else:
            raise Exception('Parsing error:%s' % line)

    # Add extra header if possible.
    email_headers = {**email_headers, **extra_header}

    return email_headers


def decode_headers(mail_as_bytes) -> CaseInsensitiveDict:
    def _decode_header(header_as_string):
        result = ''

        for i in decode_header(header_as_string):
            _bytes, charset = i
            charset = charset or 'utf-8'
            if isinstance(_bytes, bytes):
                try:
                    result += _bytes.decode(charset)
                except UnicodeDecodeError:
                    logger.warning('UnicodeDecodeError:{} {}'.format(_bytes, charset))
            elif isinstance(_bytes, str):
                result += _bytes
            else:
                raise Exception('Can not decode header:{}'.format(header_as_string))
        return result

    def _fmt_date(date_as_string):
        """Format mail header Date for humans."""
        _month = {
            'Jan': 1,
            'Feb': 2,
            'Mar': 3,
            'Apr': 4,
            'May': 5,
            'Jun': 6,
            'Jul': 7,
            'Aug': 8,
            'Sep': 9,
            'Oct': 10,
            'Nov': 11,
            'Dec': 12,
        }
        pattern_one = r'(\w+),\s+([0-9]+)\s+(\w+)\s+([0-9]+)\s+([:0-9]+)\s+(.+)'
        pattern_two = r'([0-9])\s+([\w]+)\s+([0-9]+)\s+([:0-9]+)\s+(.+)'
        match_one = re.search(pattern_one, date_as_string)
        match_two = re.search(pattern_two, date_as_string)
        if match_one:
            week, day, month_as_string, year, now_time, time_zone = match_one.groups()
            month = [v for k, v in _month.items() if month_as_string.lower() == k.lower()][0]
            return '{}-{}-{} {} {}'.format(int(year), int(month), int(day), now_time, time_zone)
        elif match_two:
            day, month_as_string, year, now_time, time_zone = match_two.groups()
            month = [v for k, v in _month.items() if month_as_string.lower() == k.lower()][0]
            return '{}-{}-{} {} {}'.format(int(year), int(month), int(day), now_time, time_zone)
        else:
            logger.warning('Can not parse Date:{}'.format(date_as_string))
            return date_as_string

    # Set default values.
    headers = CaseInsensitiveDict()
    for i in ('subject', 'from', 'to', 'date', 'content-type', 'boundary'):
        headers.setdefault(i, None)
    headers['charset'] = 'utf-8'
    # Update values by parse headers.
    _parsed_headers = parse_header(mail_as_bytes, 'boundary', 'charset', 'content-transfer-encoding')
    parsed_headers = _parsed_headers.copy()
    for k, v in _parsed_headers.items():
        if v is None:
            parsed_headers.pop(k)
    headers.update(parsed_headers)

    # Convert charset to str for subsequent parsing.
    if isinstance(headers['charset'], bytes):
        headers['charset'] = headers['charset'].decode()

    # Decode values use its charset.
    # 'boundary' need to be bytes for subsequent parsing.
    # 'charset' is already str.
    for k, v in headers.lower_items():
        if headers[k] and k not in ('boundary', 'charset'):
            try:
                headers[k] = v.decode(headers['charset'])
            except UnicodeDecodeError:
                if k in ('subject', 'from', 'to'):
                    try:
                        headers[k] = v.decode('utf-8')
                    except UnicodeDecodeError:
                        logger.critical(
                            'Can not decode basic "{}",Use {} instead, raw:{}'.format(k, 'Unknown%s' % k,
                                                                                      headers[k]))
                        headers[k] = 'Unknown%s' % k
                else:
                    logger.warning('Can not decode {} {}'.format(k, headers['charset']))
    # Decode headers for read.
    # Usually, subject|from|to need to be decode again.
    for k in ('subject', 'from', 'to'):
        if headers[k]:
            headers[k] = _decode_header(headers[k])

    # Decode 'date' for read.
    if headers.get('date'):
        headers['date'] = _fmt_date(headers['date'])

    # Warning if failed to catch basic mail elements .
    for i in ('subject', 'date', 'from', 'to', 'content-type'):
        if headers[i] is None:
            logger.warning("Can not get element '%s' in this mail." % i)

    # Headers init is complete.
    return headers


class MailDecode:
    def __init__(self, mail_as_bytes, which=None):
        """
        Mail content:
        - headers content (generated from mail headers)
        'subject'                   basic. default None.
        'from'                      basic. default None.
        'to'                        basic. default None.
        'date'                      basic. default None.
        'content-type'              basic. default None.
        'content-transfer-encoding' extra. default None.
        'boundary'                  extra. default None.
        'charset'                   extra. default 'utf-8'.

        - result content (generated from mail parsing)
        'id'                        extra. from mail server.
        'content'                   extra. default None.
        'content-html'              extra. default None.
        'attachments'               extra. default None.
        'headers'                   basic. all headers can be parsed from mail, include processed headers content.

        - raw (mail itself)
        'raw'                       basic. mail itself as raw.
        """

        self.mail_as_bytes = mail_as_bytes
        self.body_as_bytes = None
        self.headers = None
        self.id = which
        self.result = None

    def get_decoded_result(self):

        self.headers = decode_headers(self.mail_as_bytes) if self.headers is None else self.headers

        # Make result init.
        self.result = dict()
        for k in ('subject', 'from', 'to', 'date', 'content-type', 'boundary', 'charset'):
            self.result[k] = self.headers.get(k)
        for k in ('attachments', 'content', 'content-html'):
            self.result.setdefault(k, None)

        self.result['id'] = self.id
        self.result['headers'] = self.headers
        self.result['raw'] = self.mail_as_bytes

        # Get body_as_bytes
        self.body_as_bytes = None
        for line in self.mail_as_bytes:
            if line in (b'\r\n', b''):
                self.body_as_bytes = self.mail_as_bytes[self.mail_as_bytes.index(line) + 1:]
        assert self.body_as_bytes is not None, 'Can not divide headers and body.'

        # Set mail attributes.
        self.content_transfer_encoding = self.headers.get('content-transfer-encoding')
        try:
            self.content_type = re.search(r'\s?([a-z0-9]+/[a-z0-9]+)\s?;.+', self.headers['content-type']).group(1)
        except AttributeError:
            self.content_type = ''
        self.charset = self.headers.get('charset')
        self.boundary = self.headers.get('boundary')

        # Attribute check.
        if self.content_transfer_encoding is not None and self.content_transfer_encoding.lower() not in (
                'quoted-printable', '8bit', '7bit', 'base64'):
            raise Exception("Unknown encoding:{}".format(self.content_transfer_encoding))

        if self.is_multiple_part():
            self.multiple_part_decode()
        else:
            _content, _content_html = self.one_part_decode()
            self.result['content'], self.result['content-html'] = _content, _content_html

        # Compatible between content_html and content-html TODO
        self.result['content_html'] = self.result['content-html']
        return self.result

    @staticmethod
    def divide_into_parts(bytes_list, sep):
        """Divide a list of bytes to parts.
        """
        is_part = False
        result = []

        part = []
        for i in bytes_list:
            if i.find(sep) > -1:
                is_part = True
                if part:
                    result.append(part)
                part = []
                continue

            if is_part:
                part.append(i)

        return result

    def is_multiple_part(self):
        return self.headers.get('boundary')

    def multiple_part_decode(self):
        attachments = []
        content = []
        content_html = []

        parts = self.divide_into_parts(self.body_as_bytes, self.boundary)

        for part in parts:
            # Init headers.
            part_headers = CaseInsensitiveDict()
            part_headers.update(parse_header(part, 'charset'))
            part_headers['charset'] = part_headers['charset'] if part_headers.get('charset') else 'utf-8'
            if isinstance(part_headers['charset'], bytes):
                part_headers['charset'] = part_headers['charset'].decode()
            # Convert headers to string by its charset.
            for k, v in part_headers.lower_items():
                if part_headers[k] and k != 'charset':
                    try:
                        part_headers[k] = v.decode(part_headers['charset'])
                    except UnicodeDecodeError:
                        logger.warning('UnicodeDecodeError {} {} {}'.format(k, v, part_headers['charset']))
            # Divide body and headers
            part_body_as_bytes = None
            for line in part:
                if line in (b'\r\n', b''):
                    part_body_as_bytes = part[part.index(line) + 1:]
            # Empty part.
            if part_body_as_bytes is None:
                logger.info('Detect an empty part.')
                continue
            # Set part headers.
            content_transfer_encoding = part_headers.get('content-transfer-encoding')
            content_disposition = part_headers.get('content-disposition')
            try:
                content_type = re.search(r'\s?([a-z0-9]+/[a-z0-9]+)\s?;.+', part_headers['content-type']).group(1)
            except AttributeError:
                content_type = ''
            charset = part_headers.get('charset')

            # Only 3 situations: attachments,content,content_html
            # Is attachment.
            if content_disposition and content_disposition.find('attachment') > -1:
                attachment = []
                filename = re.search(r"""attachment;[\s]?filename=[\s"']?([^"';]+)""", content_disposition).group(1)
                decoded_filename = ''.join(
                    [i[0] if isinstance(i[0], str) else i[0].decode(i[1]) for i in decode_header(filename)])
                attachment.append(decoded_filename + ';%s' % content_type)

                # Add body.
                is_body = False
                for line in part:
                    if line == b'':
                        is_body = True
                        continue
                    if is_body:
                        if content_transfer_encoding.find('base64') > -1:
                            attachment.append(base64.b64decode(line))
                        else:
                            attachment.append(line)
                attachments.append(attachment)
            elif content_type in ('text/plain', 'text/html'):
                _content, _content_html = self.part_decode(part_body_as_bytes, content_transfer_encoding, content_type,
                                                           charset)
                for i in _content:
                    content.append(i)
                for i in _content_html:
                    content_html.append(i)
            else:
                logger.warning('Can not parse:{}'.format(content_type))

        self.result['content'] = content
        self.result['content-html'] = content_html
        self.result['attachments'] = attachments

    def one_part_decode(self):

        _content = []
        if self.content_transfer_encoding is None or self.content_transfer_encoding.lower() not in (
                'base64', 'quoted-printable'):
            for i in self.body_as_bytes:
                _content.append(i.decode(self.charset))
        if self.content_transfer_encoding == 'base64':
            _temp = b''
            for i in self.body_as_bytes:
                _temp += i
            _temp = base64.b64decode(_temp).decode(self.charset)
            _content.append(_temp)
        elif self.content_transfer_encoding == 'quoted-printable':
            _temp = b''
            for i in self.body_as_bytes:
                _temp += (quopri.decodestring(i))
            _temp = _temp.decode(self.charset)
            _content.append(_temp)
        if self.content_type == 'text/plain':
            return _content, None
        elif self.content_type == 'text/html':
            return None, _content
        else:
            raise Exception('Unknown content-type:{}'.format(self.content_type))

    @staticmethod
    def part_decode(body_as_bytes, content_transfer_encoding, content_type, charset):
        """Decode 'text/html' & 'text/plain' . """
        _content = []
        if content_transfer_encoding is None or content_transfer_encoding.lower() not in (
                'base64', 'quoted-printable'):
            for i in body_as_bytes:
                _content.append(i.decode(charset))
        if content_transfer_encoding == 'base64':
            _temp = b''
            for i in body_as_bytes:
                _temp += i
            _temp = base64.b64decode(_temp).decode(charset)
            _content.append(_temp)
        elif content_transfer_encoding == 'quoted-printable':
            _temp = b''
            for i in body_as_bytes:
                _temp += (quopri.decodestring(i))
            _temp = _temp.decode(charset)
            _content.append(_temp)
        if content_type == 'text/plain':
            return _content, []
        elif content_type == 'text/html':
            return [], _content
        else:
            raise Exception('Unknown content-type:{}'.format(content_type))
