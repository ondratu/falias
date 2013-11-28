def uni(text):
    """ automatic conversion from str to unicode with utf-8 encoding """
    if isinstance(text, str):
        return unicode(text, encoding = 'utf-8')
    return unicode(text)
