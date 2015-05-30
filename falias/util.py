def uni(text):
    """ automatic conversion from str to unicode with utf-8 encoding """
    if isinstance(text, str):
        return unicode(text, encoding = 'utf-8')
    return unicode(text)

def nuni(val):
    if val is None:
        return None
    return uni(val)

def nint(val):
    if val is None:
        return None
    return int(val)

def islistable(arg):
    return isinstance(arg, list) or isinstance(arg, tuple) or isinstance(arg, set)

def isnumber(arg):
    return isinstance(arg, float) or isinstance(arg, int) or isinstance(arg, long)

def uniq(l):
    n = []
    for it in l:
        if it not in n:
            n.append(it)
    return n
#enddef

class Object(object):
    """ Simple object with __contains__ method, so 'prop' in obj will work """
    def __contains__(self, key):
        return self.__dict__.__contains__(key)


class Size(object):
    """ Simple size object, which store size in width and height variable.
        Size must be set in text as WIDTHxHEIGHT
    """
    def __init__(self, text):
        self.width, self.height = tuple(int(x) for x in text.split('x'))

    def __str__(self):
        return "%dx%d" % (self.width, self.height)

    def get(self):
        return (self.width, self.height)


class Paths(tuple):
    def __init__(self, value):
        if value:
            super(tuple, self).__init__(uni(it.strip()) for it in uni(value).split(':'))
        else:
            super(tuple, self)


    def __str__(self):
        return ':'.join(self)
