"""Security library is based on smartsalt function which salt text depend on
input text.
"""
from hashlib import md5, sha1
from random import randrange, seed

seed()

# character array for crypt_md5_salt function
CCHARS = "./"
CCHARS += "".join(chr(c) for c in range(ord("a"), ord("z")))
CCHARS += "".join(chr(c) for c in range(ord("A"), ord("Z")))
CCHARS += "".join(chr(c) for c in range(ord("0"), ord("9")))
CLEN = len(CCHARS)


def smartsalt(text):
    """Return salted text depend on text."""
    ln = len(text)

    text += (ln % 2) * ("1@"+text[0])               # salt on end
    text = ((ln+1) % 2) * (text[-1]+"!V") + text    # salt on begin

    cs = 0
    for i in text:
        cs += ord(i)                      # salt in middle
    return text[ln/2:] + ((cs % 2)+1) * (text[ln/2]+"\xc5\xaf%8") + text[:ln/2]


def sha1_sdigest(text):
    """sha1 hexdigest shortcut for salted text."""
    return sha1(smartsalt(text)).hexdigest()


def md5_sdigest(text):
    """md5 hexdigest shortcut for salted text."""
    return md5(smartsalt(text)).hexdigest()


def crypt_md5_salt():
    """Return random md5 salt for crypt.crypt function."""
    return "$1$" + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        CCHARS[randrange(CLEN)] + \
        "$"
