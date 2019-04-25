"""
zmail.structures
~~~~~~~~~~~~~~~~
Data structures that power zmail.
"""
from .compat import Mapping, MutableMapping, OrderedDict


class CaseInsensitiveDict(MutableMapping):
    """A case-insensitive ``dict``-like object.
    Inspired by requests.structures

    _store -> 'key.lower()' : ('key','value')
    """

    def __init__(self, data=None, **kwargs):
        self._store = OrderedDict()
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (casedkey for casedkey, _ in self._store.values())

    def __len__(self):
        return len(self._store)

    def lower_items(self):
        """Like iteritems(), but with all lowercase keys."""
        return (
            (lowerkey, value[1])
            for (lowerkey, value)
            in self._store.items()
        )

    def __eq__(self, other):
        if isinstance(other, Mapping):
            other = CaseInsensitiveDict(other)
        else:
            return NotImplemented
        # Compare insensitively
        return dict(self.lower_items()) == dict(other.lower_items())

    def copy(self):
        """Shallow copy."""
        return CaseInsensitiveDict(self._store.values())

    def __repr__(self):
        return str(dict(self.items()))
