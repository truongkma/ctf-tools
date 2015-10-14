from Crypto.Cipher import AES
from Crypto.Util import Counter
import base64
import string
import util
import zlib

sessionid = 'TmV2ZXIgcmV2ZWFsIHRoZSBXdS1UYW5nIFNlY3JldCE='

def format_request(P):
    return '''POST / HTTP/1.1
Host: hapless.com
Cookie: sessionid={0}
Content-Length: {1}
{2}'''.format(sessionid, len(P), P)

def oracle_ctr(P):
    request = format_request(P)
    compressed_request = zlib.compress(request.encode('ascii'))
    key = util.randbytes(16)
    ctr = Counter.new(128)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    encrypted_request = cipher.encrypt(compressed_request)
    return len(encrypted_request)

def oracle_cbc(P):
    request = format_request(P)
    compressed_request = zlib.compress(request.encode('ascii'))
    key = util.randbytes(16)
    iv = util.randbytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_request = cipher.encrypt(util.padPKCS7(compressed_request, 16))
    return len(encrypted_request)

alphabet = string.ascii_letters + string.digits + '+/='

paddingAlphabet = '!@#$%^&*()-`~[]{}'

def getPadding(oracle, s):
    l = oracle(s)
    padding = ''
    for i in range(len(paddingAlphabet)):
        padding += paddingAlphabet[i]
        il = oracle(padding + s)
        if il > l:
            return padding

def guessNextByte(oracle, knownStr):
    min_ch = ''
    min_ch_sz = 0
    padding = getPadding(oracle, ('sessionid=' + knownStr + '~') * 8)
    for i in range(len(alphabet)):
        ch = alphabet[i]
        s = 'sessionid=' + knownStr + ch
        sz = oracle(padding + s * 8)
        if min_ch == '' or sz < min_ch_sz:
            min_ch = ch
            min_ch_sz = sz
    return min_ch

def recover_sessionid(oracle):
    knownStr = ''
    for i in range(0, 44):
        knownStr += guessNextByte(oracle, knownStr)
    return knownStr

recovered_sessionid = recover_sessionid(oracle_ctr)
if recovered_sessionid != sessionid:
    raise Exception(recovered_sessionid + ' != ' + sessionid)
print(base64.b64decode(recovered_sessionid))

recovered_sessionid = recover_sessionid(oracle_cbc)
if recovered_sessionid != sessionid:
    raise Exception(recovered_sessionid + ' != ' + sessionid)
print(base64.b64decode(recovered_sessionid))
