"""
zmail.message
~~~~~~~~~~~~
This module provides functions to handles MIME object.
"""
import os
import re
import mimetypes
import logging
import quopri
import base64

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.header import decode_header

from .utils import type_check, get_abs_path, make_iterable, bytes_to_string, str_decode
from .structures import CaseInsensitiveDict

logger = logging.getLogger('zmail')


def mail_encode(message):
    """Convert a dict to a MIME obj."""
    logger.info('Encoding mail to MIME obj.')

    # Type check.
    type_check(dict, message)

    # Create MIMEMultipart.
    msg = MIMEMultipart()

    # Set basic email elements.
    for k, v in message.items():
        if k.capitalize() in ('From', 'To', 'Subject') and v:
            msg[k.capitalize()] = v

    # Set extra parameters.
    for k in message:
        if k.capitalize() not in ('From', 'To', 'Subject') and k not in ('attachments', 'content'):
            msg[k] = message[k]

    # Set mail content.
    if 'content_html' in message:
        msg.attach(MIMEText('%s' % message['content_html'], 'html', 'utf-8'))
    if 'content' in message:
        _message = make_iterable(message['content'])
        _combine_message = ''
        for i in _message:
            _combine_message += i
        msg.attach(MIMEText('{}'.format(_combine_message), 'plain', 'utf-8'))

    # Set attachments.
    if 'attachments' in message and message['attachments']:
        attachments = make_iterable(message['attachments'])
        for attachment in attachments:
            logger.info('Loading %s', attachment)
            attachment = get_abs_path(attachment)
            part = _get_attachment_part(attachment)
            msg.attach(part)

    return msg


def mail_decode(mail_as_bytes, which=1):
    """Convert a MIME bytes to dict."""
    return MailDecode(mail_as_bytes, which).result


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


def _get_attachment_part(file):
    """According to file-type return a prepared attachment part."""
    name = os.path.split(file)[1]
    file_type = mimetypes.guess_type(name)[0]

    if file_type is None:
        logger.warning('Could not guess %s type, use application type instead.', file)
        file_type = 'application/octet-stream'

    main_type, sub_type = file_type.split('/')

    if main_type == 'text':
        with open(file, 'r') as f:
            part = MIMEText(f.read())
            part['Content-Disposition'] = 'attachment;filename="%s"' % name

    elif main_type in ('image', 'audio'):
        with open(file, 'rb') as f:
            part = MIMEImage(f.read(), _subtype=sub_type) if main_type == 'image' else \
                MIMEAudio(f.read(), _subtype=sub_type)
            part['Content-Disposition'] = 'attachment;filename="%s"' % name
    else:
        with open(file, 'rb') as f:
            part = MIMEBase(main_type, sub_type)
            part.set_payload(f.read())
            part['Content-Disposition'] = 'attachment;filename="%s"' % name
            encode_base64(part)

    return part


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
    date_list = date_as_string.split(',')
    try:
        date_list = date_list[1].split(' ')
    except IndexError:
        return date_as_string

    date_list = list(filter(lambda x: x != '', date_list))
    day = date_list[0]
    month = _month[date_list[1]]
    year = date_list[2]
    times = date_list[3]
    time_zone = date_list[4]

    return '{}-{}-{} {} {}'.format(year, month, day, times, time_zone)


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


def parse_header_shortcut(mail_as_bytes):
    """Shortcut for parse mail headers(only)."""
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

    # Warning failed to catch basic mail elements .
    for i in ('subject', 'date', 'from', 'to', 'content-type'):
        if headers[i] is None:
            logger.warning("Can not get element '%s' in this mail." % i)
    return headers


class MailDecode:
    def __init__(self, mail_as_bytes, which):
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
                headers[k] = self._decode_header(headers[k])

        # Decode 'date' for read.
        if headers.get('date'):
            headers['date'] = _fmt_date(headers['date'])

        # Warning failed to catch basic mail elements .
        for i in ('subject', 'date', 'from', 'to', 'content-type'):
            if headers[i] is None:
                logger.warning("Can not get element '%s' in this mail." % i)

        # Headers init is complete.
        self.headers = headers

        # Make result init.
        self.result = dict()
        for k in ('subject', 'from', 'to', 'date', 'content-type', 'boundary', 'charset'):
            self.result[k] = headers.get(k)
        for k in ('attachments', 'content', 'content_html'):
            self.result.setdefault(k, None)

        self.result['id'] = which
        self.result['headers'] = headers
        self.result['raw'] = mail_as_bytes

        # Get body_as_bytes
        self.body_as_bytes = None
        for line in mail_as_bytes:
            if line in (b'\r\n', b''):
                self.body_as_bytes = mail_as_bytes[mail_as_bytes.index(line) + 1:]
        assert self.body_as_bytes is not None, 'Can not divide headers and body.'

        # Set mail attributes.
        self.content_transfer_encoding = headers.get('content-transfer-encoding')
        self.content_type = re.search(r'\s?([a-z0-9]+/[a-z0-9]+)\s?;.+', headers['content-type']).group(1)
        self.charset = headers.get('charset')
        self.boundary = headers.get('boundary')

        # Attribute check.
        if self.content_transfer_encoding is not None and self.content_transfer_encoding.lower() not in (
                'quoted-printable', '8bit', '7bit', 'base64'):
            raise Exception("Unknown encoding:{}".format(self.content_transfer_encoding))

        if self.is_multiple_part():
            self.multiple_part_decode()
        else:
            _content, _content_html = self.one_part_decode()
            self.result['content'], self.result['content_html'] = _content, _content_html

    @staticmethod
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

    def is_multiple_part(self):
        return self.headers.get('boundary')

    def multiple_part_decode(self):
        attachments = []
        content = []
        content_html = []

        parts = divide_into_parts(self.body_as_bytes, self.boundary)

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
                attachment.append(filename + ';%s' % content_type)

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
        self.result['content_html'] = content_html
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
