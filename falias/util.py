def uni(text):
    """ automatic conversion from str to unicode with utf-8 encoding """
    if isinstance(text, str):
        return unicode(text, encoding = 'utf-8')
    return unicode(text)

def islistable(arg):
    return isinstance(arg, list) or isinstance(arg, tuple) or isinstance(arg, set)

def isnumber(arg):
    return isinstance(arg, float) or isinstance(arg, int) or isinstance(arg, long)
