"""
zmail.message
~~~~~~~~~~~~
This module provides a MailMessage object to handles MIME object.
"""
import os
import mimetypes
import logging

from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64

from .utils import type_check, get_abs_path, make_iterable

logger = logging.getLogger('zmail')


class MailMessage:
    """This object handles MIME object."""
    _basic = ('From', 'To', 'Subject')

    def __init__(self):
        logger.info('Initiate MailMessage.')

    def encode(self, message):
        """Convert a dict to a MIME obj."""
        logger.info('Encoding mail to MIME obj.')

        # Type check.
        type_check(dict, message)

        # Create MIMEMultipart.
        msg = MIMEMultipart()

        # Set basic email elements.
        for k, v in message.items():
            if k.capitalize() in self._basic and v:
                msg[k.capitalize()] = v

        # Set extra parameters.
        for k in message:
            if k.capitalize() not in self._basic and k not in ('attachments', 'content'):
                msg[k] = message[k]

        # Set mail content.
        msg.attach(MIMEText('%s' % message['content'], 'plain', 'utf-8'))

        # Set attachments.
        if 'attachments' in message and message['attachments']:
            attachments = make_iterable(message['attachments'])
            for attachment in attachments:
                logger.info('Loading %s', attachment)
                attachment = get_abs_path(attachment)
                part = self._get_attachment_part(attachment)
                msg.attach(part)

        return msg

    def decode(self):
        """Convert a MIME string to dict."""
        pass

    @staticmethod
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
