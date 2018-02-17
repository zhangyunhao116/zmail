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

_basic = ('From', 'To', 'Subject')


def mail_encode(message):
    """Convert a dict to a MIME obj."""
    logger.info('Encoding mail to MIME obj.')

    # Type check.
    type_check(dict, message)

    # Create MIMEMultipart.
    msg = MIMEMultipart()

    # Set basic email elements.
    for k, v in message.items():
        if k.capitalize() in _basic and v:
            msg[k.capitalize()] = v

    # Set extra parameters.
    for k in message:
        if k.capitalize() not in _basic and k not in ('attachments', 'content'):
            msg[k] = message[k]

    # Set mail content.
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


def mail_decode(header_as_bytes, body_as_bytes, which):
    """Convert a MIME bytes list to dict."""

    result = parse_header(header_as_bytes)

    for i in ('content', 'contents', 'attachments',):
        result.setdefault(i)
    content = None
    attachments = None

    # Add 'id'
    result['id'] = which

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
    """Parse mail header then return a dictionary include basic elements in email.

    [b'Subject: success!',b'Date:Fri, 09 Feb 2018 23:10:11 +0800 (CST)']
    ---------->
    {'subject':'success!','date': '2018-2-09 23:10:11 +0800'}

    Basic headers(must): 'Subject', 'Date', 'From', 'To', 'Content-Type' , 'boundary'

    Extra header(exist or None):

    """
    _headers = ['subject', 'date', 'from', 'to', 'content-type', 'boundary']
    if args:
        extra_header = make_iterable(args)
        for h in extra_header:
            _headers.append(h)

    headers = {}
    result = {}
    header = ''
    part = ''
    boundary = None

    # Parse header.
    for line in mail_as_bytes:
        # Get boundary if possible.
        if boundary is None:
            have_boundary = re.findall(rb'boundary=(.+)?', line)
            if len(have_boundary):
                boundary = have_boundary[0]
                if boundary[0] == 34:
                    boundary = boundary[1:]
                if boundary[-1] == 34:
                    boundary = boundary[:-1]

        # Header boundary check.
        if line == b'':
            headers[header.lower()] = part
            break
        if re.fullmatch(rb'([a-zA-Z-]+):\s?.+?', line):
            # Line is a header.
            if part and header:
                headers[header.lower()] = part
            header = re.findall(rb'([a-zA-Z-]+):\s?', line)[0].decode()
            part = line.split(header.encode() + b':')[1]
        else:
            # Line is a part of header.
            part += line

    headers['boundary'] = boundary if boundary else None

    for k, v in headers.items():
        if k in _headers:
            result[k] = v

    # Encoding ('from', 'to', 'subject', 'content-type').
    for k, v in result.items():
        if k in ('from', 'to', 'subject', 'content-type') and v:
            v_decoded = ''
            v_list = decode_header(v.decode())
            for j in v_list:
                if j[1] is None:
                    v_decoded += str_decode(j[0])
                else:
                    v_decoded += str_decode(j[0], j[1])
            result[k] = v_decoded

    # Format time.
    result['date'] = _fmt_date(result['date'])

    return result


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
        headers = {}
        header = ''
        part = ''
        # Parse each part's header.
        for line in p:
            # Header boundary check.
            if line == b'':
                headers[header] = part
                break
            if re.fullmatch(rb'.+:\s?.+?', line):
                # Line is a header.
                if part and header:
                    headers[header] = part
                header = re.findall(rb'(.+):\s?', line)[0].decode()
                part = line.split(header.encode() + b':')[1]
            else:
                # Line is a part of header.
                part += line
        # Is attachment.
        if headers.get('Content-Disposition') and headers['Content-Disposition'].find(b'attachment') == 0:
            attachment = []
            coding = headers['Content-Transfer-Encoding']
            filename = re.findall(rb'attachment;\s?filename=(.+|".+")', headers['Content-Disposition'])[0]
            filename = filename.decode()
            # Fix " [could be improved]
            if filename[0] == '"':
                filename = filename[1:]
            if filename[-1] == '"':
                filename = filename[:-1]

            attachment.append(filename + ';%s' % headers['Content-Type'].decode())
            # Add body.
            is_body = False
            for line in p:
                if line == b'':
                    is_body = True
                    continue
                if is_body:
                    if coding.find(b'base64') > -1:
                        attachment.append(base64.b64decode(line))
                    else:
                        attachment.append(line)
            attachments.append(attachment)

        # Is text/plain.
        elif headers['Content-Type'].find(b'text/plain') > -1:
            logger.info('Parse text/plain part,coding:{}'.format(headers['Content-Transfer-Encoding']))
            is_body = False
            coding = headers['Content-Transfer-Encoding']
            for line in p:
                if line == b'':
                    is_body = True
                    continue
                if is_body:
                    if coding.find(b'base64') > -1:
                        content.append(base64.b64decode(line).decode())
                    else:
                        content.append(line.decode())
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
