from hashlib import sha1, md5

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
