from hashlib import sha1, md5
from random import seed, randrange

seed()

cchars  = './'
cchars += ''.join(chr(c) for c in xrange(ord('a'),ord('z')))
cchars += ''.join(chr(c) for c in xrange(ord('A'),ord('Z')))
cchars += ''.join(chr(c) for c in xrange(ord('0'),ord('9')))
clen = len(cchars)

def smartsalt(text):
    ln = len(text)
    
    text += (ln % 2) * ('1@'+text[0])               # salt on end
    text = ((ln+1) % 2) * (text[-1]+'!V') + text    # salt on begin

    cs = 0
    for i in text: cs+= ord(i)                      # salt in middle
    text = text[ln/2:] + ((cs % 2)+1) * (text[ln/2]+'\xc5\xaf%8') + text[:ln/2]

    return text
#enddef

def sha1_sdigest(text):
    return sha1(smartsalt(text)).hexdigest()

def md5_sdigest(text):
    return md5(smartsalt(text)).hexdigest()

def crypt_md5_salt():
    """ Return random md5 salt for crypt.crypt function. """
    return '$1$' + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            cchars[randrange(clen)] + \
            '$'
#enddef
