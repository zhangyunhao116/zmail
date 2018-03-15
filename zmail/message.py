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
        msg.attach(MIMEText('%s' % message['content'], 'plain', 'utf-8'))

    # Set attachments.
    if 'attachments' in message and message['attachments']:
        attachments = make_iterable(message['attachments'])
        for attachment in attachments:
            logger.info('Loading %s', attachment)
            attachment = get_abs_path(attachment)
            part = _get_attachment_part(attachment)
            msg.attach(part)

    return msg


def mail_decode(mail_as_bytes, which):
    """Convert a MIME bytes to dict."""
    result = {}

    # Init.
    for i in ('content', 'contents', 'attachments',):
        result.setdefault(i)
    content = None
    attachments = None

    # Parse headers.
    headers = parse_header(mail_as_bytes, 'boundary')
    result['header'] = headers

    # Add id.
    result['id'] = which

    # Try get ('subject', 'date', 'from', 'to', 'content-type', 'boundary')
    _basic = {'subject': 'Subject', 'date': 'Date', 'from': 'From', 'to': 'To',
              'content-type': 'Content-Type', 'boundary': 'boundary'}
    for k, v in _basic.items():
        try:
            result[k] = headers[v]
        except KeyError:
            result[k] = None
            logger.warning('Can not get element %s in this mail.' % v)
    # Get body.
    body_as_bytes = None
    for line in mail_as_bytes:
        if line in (b'\r\n', b''):
            body_as_bytes = mail_as_bytes[mail_as_bytes.index(line):]
    assert body_as_bytes is not None, 'Can not divide header and body'

    # Decode multi-part mail or one-part mail.
    if result['boundary']:
        logger.info('Decoding multi-part body.id:{},{}'.format(result['id'], result['boundary']))
        body, content, attachments = multiple_part_decode(body_as_bytes, result['boundary'])
    else:
        logger.info('Decoding one-part body.id:{}'.format(result['id']))
        body = one_part_decode(body_as_bytes, result['content-type'])
        if result['content-type'] == 'text/plain':
            result['content'] = body

    result['contents'] = body

    # Add content|attachment if possible

    if content:
        result['content'] = content
    if attachments:
        result['attachments'] = attachments

    return result


def parse_header(mail_as_bytes, *args):
    """Parse mail header then return a dictionary include basic elements in email."""
    email_headers = {}

    # Parse headers.
    extra_header = {}
    for i in args:
        extra_header[i] = None
    extra_pattern = rb"""[\s]?=["'\s]?([^"';\r\n\s]+)["';\r\n\s]?"""

    part = b''
    header = b''

    for line in mail_as_bytes:
        # Get extra_header if possible.
        for k, v in extra_header.items():
            if v is None and re.search(bytes(k, encoding='utf8') + extra_pattern, line):
                extra_header[k] = re.search(bytes(k, encoding='utf8') + extra_pattern, line).group(1)

        # Parsing header.
        if re.fullmatch(rb'([0-9a-zA-Z-]+):\s?([^\r\n]+)[\r\n]?', line):
            # Line is a header.
            if part and header:
                email_headers[header.decode()] = part
            header, part = re.search(rb'([0-9a-zA-Z-]+):\s?([^\r\n]+)[\r\n]?', line).group(1, 2)
        elif re.fullmatch(rb'[\t]?([^\r\n]+)[\r\n]?', line):
            # Line is a part of header.
            _part = re.search(rb'[\t]?([^\r\n]+)[\r\n]?', line).group(1)
            part += _part
        elif line in (b'\r\n', b''):
            # Mail header boundary.
            if part and header:
                email_headers[header.decode()] = part
            break
        else:
            raise Exception('Parsing error:%s' % line)

    # Decode headers.
    for k, v in email_headers.items():
        groups = decode_header(v.decode())
        string = ''
        for group in groups:
            _string, charset = group
            string += str_decode(_string, charset)
        email_headers[k] = string

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


def _fmt_date(date_as_bytes):
    """Format mail header Date for humans."""
    date_as_string = date_as_bytes.decode()

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
    # week = date_list[0].replace(' ', '')
    date_list = date_list[1].split(' ')

    date_list = list(filter(lambda x: x != '', date_list))
    day = date_list[0]
    month = _month[date_list[1]]
    year = date_list[2]
    times = date_list[3]
    time_zone = date_list[4]

    return '{}-{}-{} {} {}'.format(year, month, day, times, time_zone)


def multiple_part_decode(body_as_bytes, boundary):
    """Convert MIME body to content."""
    # Get part|content|attachments if possible.
    attachments = []
    content = []
    parts = []

    # Divide into multiple parts.
    is_part = False
    part = []
    for i in body_as_bytes:

        if i.find(boundary) > -1:
            is_part = True
            if part:
                parts.append(part)
            part = []
            continue

        if is_part:
            part.append(i)

    # Parse each parts.
    for p in parts:
        # Parse each part's header.
        headers = parse_header(p, 'charset')

        content_type = headers['Content-Type'] if headers.get('Content-Type') else None
        encoding = headers['Content-Transfer-Encoding'] if headers.get('Content-Transfer-Encoding') else None
        disposition = headers['Content-Disposition'] if headers.get('Content-Disposition') else None
        charset = headers['charset'] if headers.get('charset') else None

        # Is attachment.
        if disposition and disposition.find('attachment') == 0:
            attachment = []
            filename = re.search(r"""attachment;[\s]?filename=[\s"']?([^"';]+)""", disposition).group(1)
            attachment.append(filename + ';%s' % content_type)

            # Add body.
            is_body = False
            for line in p:
                if line == b'':
                    is_body = True
                    continue
                if is_body:
                    if encoding.find('base64') > -1:
                        attachment.append(base64.b64decode(line))
                    else:
                        attachment.append(line)
            attachments.append(attachment)

        # Is text.
        elif headers.get('Content-Type'):
            logger.info('Parse {},coding:{}'.format(headers['Content-Type'], headers['Content-Transfer-Encoding']))
            is_body = False
            coding = headers['Content-Transfer-Encoding']
            for line in p:
                if line == '':
                    is_body = True
                    continue
                if is_body:
                    if coding.find('base64') > -1:
                        content.append(base64.b64decode(line).decode())
                    else:
                        content.append(line.decode())
        else:
            raise Exception('Multiple part error!')

    return parts, content, attachments


def one_part_decode(body_as_bytes, content_type):
    # [could be improved]
    body_as_string = bytes_to_string(body_as_bytes)
    body = ''

    # Could't decode.
    if content_type != 'text/plain':
        logger.info("Could't decode body, use raw instead.Type:{}".format(content_type))
        body = []
        for i in body_as_string:
            if len(i) == 74:
                body.append(i[:-1])
            else:
                body.append(i)
        return body

    # Type is 'text/plain'.
    for i in body_as_string:
        if len(i) == 74 and i[-1] == '=':
            body += quopri.decodestring(i[:-1]).decode()
        else:
            body += quopri.decodestring(i).decode()
    return body
