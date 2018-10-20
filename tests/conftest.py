import json
import os

import pytest


@pytest.fixture(scope='module')
def here():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='module')
def accounts(here):
    accounts_path = os.path.join(here, 'config')

    with open(accounts_path, 'r') as f:
        raw = f.read()

    return json.loads(raw)
