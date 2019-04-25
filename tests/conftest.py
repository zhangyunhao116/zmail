import json
import os
from typing import List, Tuple

import pytest


@pytest.fixture(scope='module')
def here():
    return os.path.abspath(os.path.dirname(__file__))


@pytest.fixture(scope='module')
def accounts(here) -> List[Tuple] or None:
    """Return account list"""
    accounts_path = os.path.join(here, 'config')

    if not os.path.exists(accounts_path):
        return None

    with open(accounts_path, 'r') as f:
        raw = f.read()

    return json.loads(raw)
