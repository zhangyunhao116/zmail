import os

import pytest

from zmail.structures import CaseInsensitiveDict
from zmail.utils import save_attachment


def test_save_attachment(here):
    mock_mail = CaseInsensitiveDict({
        'attachments': [('_test_0.txt', b'55555'), ('_test_1.txt', b'66666')]
    })

    save_attachment(mock_mail)
    file_name_0 = mock_mail['attachments'][0][0]
    file_raw_0 = mock_mail['attachments'][0][1]
    file_name_1 = mock_mail['attachments'][1][0]
    file_raw_1 = mock_mail['attachments'][1][1]
    with open(file_name_0, 'rb') as f:
        assert f.read() == file_raw_0

    with open(file_name_1, 'rb') as f:
        assert f.read() == file_raw_1

    save_attachment(mock_mail, overwrite=True)  # No FileExistsError
    with pytest.raises(FileExistsError):
        save_attachment(mock_mail)

    os.remove(file_name_0)
    os.remove(file_name_1)

    # Test defined path.
    save_attachment(mock_mail, here)
    path_0 = os.path.join(here, file_name_0)
    path_1 = os.path.join(here, file_name_1)

    with open(path_0, 'rb') as f:
        assert f.read() == file_raw_0

    with open(path_1, 'rb') as f:
        assert f.read() == file_raw_1

    save_attachment(mock_mail, here, overwrite=True)  # No FileExistsError
    with pytest.raises(FileExistsError):
        save_attachment(mock_mail, here)

    os.remove(path_0)
    os.remove(path_1)
