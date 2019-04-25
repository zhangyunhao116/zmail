import sys

PY_37 = sys.version_info >= (3, 7)

if PY_37:
    from collections import OrderedDict  # noqa
    from collections.abc import Mapping, MutableMapping  # noqa
else:
    from collections import OrderedDict, Mapping, MutableMapping  # noqa
