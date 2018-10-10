import json
import os

here = os.path.abspath(os.path.dirname(__file__))

accounts_path = os.path.join(here, 'config')

with open(accounts_path, 'r') as f:
    raw = f.read()

accounts = json.loads(raw)
