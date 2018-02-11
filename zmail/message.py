"""
zmail.message
~~~~~~~~~~~~
This module provides a MailMessage object to handles MIME object.
"""
import os
import re
import mimetypes
import logging

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.header import decode_header

from .utils import type_check, get_abs_path, make_iterable, bytes_to_string

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


def mail_decode(mail_as_bytes):
    """Convert a MIME bytes list to dict."""
    mail_as_string = bytes_to_string(mail_as_bytes)

    # Get boundary if it's a multi/part mail.
    boundary = None
    for i in mail_as_string:
        have_boundary = re.findall(r'boundary="?(.+)"?', i)
        if len(have_boundary):
            boundary = have_boundary[0]
            break

    if boundary:
        print(boundary)
        mail = multiple_part_decode(mail_as_string, boundary)
        return mail

    return 0


def parse_header(header, _bytes=True, extra_header=None):
    """Parse mail header then return a dictionary include basic elements in email.
    ['Subject: success!','Date:Fri, 09 Feb 2018 23:10:11 +0800 (CST)']
    ---------->
    {'subject':'success!','date': '2018-2-09 23:10:11 +0800'}
    """
    _headers = ['Subject', 'Date', 'From', 'To']
    if extra_header:
        extra_header = make_iterable(extra_header)
        for h in extra_header:
            _headers.append(h)

    _string_header = bytes_to_string(header) if _bytes else header
    headers = []
    result = {}
    for i in _string_header:
        for header in _headers:
            if re.match(header, i):
                # Get basic mail headers.
                part = ''
                for section in decode_header(i):
                    if section[1] is None and isinstance(section[0], str):
                        part = part + section[0]
                    elif section[1] is None:
                        part = part + section[0].decode()
                    else:
                        part = part + section[0].decode(section[1])
                headers.append(part)

    # Convert headers list to a dictionary object.
    # Like ['Subject: success!'] -> {'subject':'success!'}
    for j in headers:
        header_split = j.split(' ')
        if len(header_split) == 2:
            result[header_split[0][:-1].lower()] = header_split[1]
        elif header_split[0][:-1] == 'Date':
            result['date'] = header_split[1:]
        else:
            result[header_split[0][:-1].lower()] = ''.join(header_split[1:])

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


def _fmt_date(date_list):
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
    day = date_list[1]
    month = _month[date_list[2]]
    year = date_list[3]
    times = date_list[4]
    time_zone = date_list[5]

    return '{}-{}-{} {} {}'.format(year, month, day, times, time_zone)


def multiple_part_decode(mail_as_string, boundary):
    return mail_as_string
