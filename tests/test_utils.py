import os
from contextlib import suppress

import pytest

from zmail.api import server
from zmail.structures import CaseInsensitiveDict
from zmail.utils import read, save, save_attachment


def test_save_attachment(here):
    mock_mail = CaseInsensitiveDict({
        'attachments': [('_test_0.txt', b'55555'), ('_test_1.txt', b'66666')]
    })
    file_name_0 = mock_mail['attachments'][0][0]
    file_raw_0 = mock_mail['attachments'][0][1]
    file_name_1 = mock_mail['attachments'][1][0]
    file_raw_1 = mock_mail['attachments'][1][1]

    path_0 = os.path.join(here, file_name_0)  # Mock user defined path.
    path_1 = os.path.join(here, file_name_1)
    try:
        save_attachment(mock_mail)

        with open(file_name_0, 'rb') as f:
            assert f.read() == file_raw_0

        with open(file_name_1, 'rb') as f:
            assert f.read() == file_raw_1

        save_attachment(mock_mail, overwrite=True)  # No FileExistsError
        with pytest.raises(FileExistsError):
            save_attachment(mock_mail)

        # Test defined path.
        save_attachment(mock_mail, here)

        with open(path_0, 'rb') as f:
            assert f.read() == file_raw_0

        with open(path_1, 'rb') as f:
            assert f.read() == file_raw_1

        save_attachment(mock_mail, here, overwrite=True)  # No FileExistsError
        with pytest.raises(FileExistsError):
            save_attachment(mock_mail, here)
    except (BaseException, Exception):
        raise
    finally:
        with suppress(FileNotFoundError):
            os.remove(file_name_0)
            os.remove(file_name_1)
            os.remove(path_0)
            os.remove(path_1)


def test_save_and_read(accounts):
    if not accounts:
        pytest.skip('Can not get accounts')

    try:
        account = accounts[0]
        username, password = account
        if server(username, password).stat()[0]:
            mail = server(username, password).get_latest()
            save(mail, name='_test.eml')
            saved_mail = read('_test.eml')
            saved_mail['id'] = mail.get('id')
            assert mail == saved_mail
    except (BaseException, Exception):
        raise
    finally:
        with suppress(FileNotFoundError):
            os.remove('_test.eml')
