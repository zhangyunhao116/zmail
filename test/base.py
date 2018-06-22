import os
import json

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'config'), 'r') as f:
    raw = f.read()

config = json.loads(raw)
