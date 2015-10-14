from Crypto.Random import random
import binascii

def invmod(a, n):
    t = 0
    newt = 1
    r = n
    newr = a
    while newr != 0:
        q = r // newr
        (t, newt) = (newt, t - q * newt)
        (r, newr) = (newr, r - q * newr)
    if r > 1:
        raise Exception('unexpected')
    if t < 0:
        t += n
    return t

smallPrimes = [2, 3, 5, 7, 11, 13, 17, 19]

def hasSmallPrimeFactor(p):
    for x in smallPrimes:
        if p % x == 0:
            return True
    return False

def isProbablePrime(p, n):
    for i in range(n):
        a = random.randint(1, p)
        if pow(a, p - 1, p) != 1:
            return False
    return True

def getProbablePrime(bitcount):
    while True:
        p = random.randint(2**(bitcount - 1), 2**bitcount - 1)
        if not hasSmallPrimeFactor(p) and isProbablePrime(p, 5):
            return p

def genKey(keysize):
    e = 3
    bitcount = (keysize + 1) // 2 + 1

    p = 7
    while (p - 1) % e == 0:
        p = getProbablePrime(bitcount)

    q = p
    while q == p or (q - 1) % e == 0:
        q = getProbablePrime(bitcount)

    n = p * q
    et = (p - 1) * (q - 1)
    d = invmod(e, et)
    pub = (e, n)
    priv = (d, n)
    return (pub, priv)

def encryptnum(pub, m):
    (e, n) = pub
    if m < 0 or m >= n:
        raise ValueError(str(m) + ' out of range')
    return pow(m, e, n)

def decryptnum(priv, c):
    (d, n) = priv
    if c < 0 or c >= n:
        raise ValueError(str(c) + ' out of range')
    return pow(c, d, n)

# Drops leading zero bytes.
def bytestonum(s):
    return int.from_bytes(s, byteorder='big')

def numtobytes(k):
    return k.to_bytes((k.bit_length() + 7) // 8, byteorder='big')

def encryptbytes(pub, mbytes):
    m = bytestonum(mbytes)
    c = encryptnum(pub, m)
    cbytes = numtobytes(c)
    return cbytes

def decryptbytes(priv, cbytes):
    c = bytestonum(cbytes)
    m = decryptnum(priv, c)
    mstr = numtobytes(m)
    return mstr

if __name__ == '__main__':
    pub, priv = genKey(128)
    m = b'test'
    c = encryptbytes(pub, m)
    m2 = decryptbytes(priv, c)
    if m != m2:
        raise Exception(str(m) + ' != ' + str(m2))
