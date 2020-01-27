"""Support library for auto convert or check types."""

from json import JSONEncoder
from sys import version_info

def nstr(val):
    """Return None or unicode."""
    if val is None:
        return None
    return str(val)


def nint(val):
    """Return None or int."""
    if val is None:
        return None
    return int(val)


def islistable(obj):
    """Return True is obj is listable."""
    return isinstance(obj, (list, tuple, set))


def isnumber(obj):
    """Return True if obj is number."""
    return isinstance(obj, (float, int))


def uniq(l):
    """Return list without duplication."""
    return list(set(l))


def dict_difference(one, two):
    """ Return new dictionary, with pairs if key from one is not in two,
        or if value of key in one is another then value of key in two.
    """
    class NotFound:
        pass
    rv = dict()
    for key, val in one.items():
        if val != two.get(key, NotFound()):
            rv[key] = val
    return rv


class Object(object):
    """ Simple object with __contains__ method, so 'prop' in obj will work """
    def __init__(self, **kwargs):
        """Set keyword arguments as object properties."""
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __contains__(self, key):
        return hasattr(self, key)

    def __json__(self):
        """Return dictionary for json.

        This method was be called by ObjectEncoder.
        """
        rv = self.__dict__.copy()
        rv['__class__'] = self.__class__.__name__
        return rv


class ObjectEncoder(JSONEncoder):
    """JSONEncoder class for Object instance.

    Call Object.__json__ method, for better json export.
    """
    def default(self, obj):
        if isinstance(obj, Object):
            return obj.__json__()
        return JSONEncoder.default(self, obj)


class Size(object):
    """ Simple size object, which store size in width and height variable.
        Size must be set in text as WIDTHxHEIGHT
    """
    def __init__(self, text):
        self.width, self.height = tuple(int(x) for x in text.split('x'))

    def __str__(self):
        return "%dx%d" % (self.width, self.height)

    def get(self):
        """Return tuple of width and height."""
        return (self.width, self.height)


class Paths(list):
    """Paths object parse string and split it with colon character."""
    def __init__(self, value):
        if value:
            super(Paths, self).__init__(
                it.strip() for it in value.split(':'))
        else:
            super(Paths, self).__init__()

    def __str__(self):
        return ':'.join(self)
