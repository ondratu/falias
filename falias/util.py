def uni(text):
    """ automatic conversion from str to unicode with utf-8 encoding """
    if isinstance(text, str):
        return unicode(text, encoding = 'utf-8')
    return unicode(text)

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
