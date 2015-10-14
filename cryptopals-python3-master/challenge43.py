from Crypto.Random import random
import binascii
import challenge39
import hashlib

def genP(L, q):
    minK = (2**(L-1) + q-1)//q
    maxK = (2**L - 1)//q
    while True:
        k = random.randint(minK, maxK)
        p = k*q + 1
        if challenge39.isProbablePrime(p, 5):
            return (k, p)

def genG(p, q, k):
    for h in range(2, p - 1):
        g = pow(h, k, p)
        if g != 1:
            return g
    raise Exception('unexpected')

def genParams(L, N):
    q = challenge39.getProbablePrime(N)
    k, p = genP(L, q)
    g = genG(p, q, k)
    return (p, q, g)

def areValidParams(L, N, p, q, g):
    return ((q.bit_length() == N) and
            challenge39.isProbablePrime(q, 5) and
            (p.bit_length() == L) and
            challenge39.isProbablePrime(p, 5) and
            ((p-1) % q == 0) and
            pow(g, q, p) == 1)

def genKeys(p, q, g):
    x = random.randint(1, q-1)
    y = pow(g, x, p)
    pub = (p, q, g, y)
    priv = x
    return (pub, priv)

def areValidKeys(pub, priv):
    (p, q, g, y) = pub
    x = priv
    return y == pow(g, x, p)

def hash(message):
    sha1 = hashlib.sha1()
    sha1.update(message)
    digest = sha1.digest()
    return int.from_bytes(digest, byteorder='big')

def signHashWithK(H, pub, priv, k):
    (p, q, g, y) = pub
    x = priv
    r = pow(g, k, p) % q
    if r == 0:
        return None
    kInv = challenge39.invmod(k, q)
    s = (kInv * (H + x * r)) % q
    if s == 0:
        return None
    return (r, s)

def signHash(H, pub, priv):
    (_, q, _, _) = pub
    while True:
        k = random.randint(1, q-1)
        signature = signHashWithK(H, pub, priv, k)
        if not signature:
            continue
        return signature

def sign(message, pub, priv):
    return signHash(hash(message), pub, priv)

def verifySignatureHash(H, signature, pub):
    (r, s) = signature
    (p, q, g, y) = pub
    if r <= 0 or r >= q or s <= 0 or s >= q:
        return False
    w = challenge39.invmod(s, q)
    u1 = (H * w) % q
    u2 = (r * w) % q
    v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q
    return v == r

def verifySignature(message, signature, pub):
    return verifySignatureHash(hash(message), signature, pub)

def extractKey(H, r, s, k, pub):
    (p, q, g, y) = pub
    rInv = challenge39.invmod(r, q)
    return (rInv * (s * k - H)) % q

def bruteForceKey(H, r, s, pub, kMin, kMax):
    for k in range(kMin, kMax):
        priv = extractKey(H, r, s, k, pub)
        if areValidKeys(pub, priv):
            return (k, priv)
    return None

if __name__ == '__main__':
    L = 1024
    N = 160
    (p, q, g) = (0x800000000000000089e1855218a0e7dac38136ffafa72eda7859f2171e25e65eac698c1702578b07dc2a1076da241c76c62d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebeac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc871a584471bb1, 0xf4f47f05794b256174bba6e9b396a7707e563c5b, 0x5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119458fef538b8fa4046c8db53039db620c094c9fa077ef389b5322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a0470f5b64c36b625a097f1651fe775323556fe00b3608c887892878480e99041be601a62166ca6894bdd41a7054ec89f756ba9fc95302291)
    message = b'''For those that envy a MC it can be hazardous to your health
So be friendly, a matter of life and death, just like a etch-a-sketch
'''
    expectedH = 0xd2d0714f014a9784047eaeccf956520045c45265
    H = hash(message)
    if H != expectedH:
        raise Exception(hex(H) + ' != ' + hex(expectedH))
    y = 0x84ad4719d044495496a3201c8ff484feb45b962e7302e56a392aee4abab3e4bdebf2955b4736012f21a08084056b19bcd7fee56048e004e44984e2f411788efdc837a0d2e5abb7b555039fd243ac01f0fb2ed1dec568280ce678e931868d23eb095fde9d3779191b8c0299d6e07bbb283e6633451e535c45513b2d33c99ea17
    r = 548099063082341131477253921760299949438196259240
    s = 857042759984254168557880549501802188789837994940
    pub = (p, q, g, y)
    if not verifySignatureHash(H, (r, s), pub):
        raise Exception('unexpected')
    k, priv = bruteForceKey(H, r, s, pub, 0, 2**16)
    expectedHashPriv = 0x0954edd5e0afe5542a4adf012611a91912a3ec16
    hashPriv = hash(hex(priv)[2:].encode('ascii'))
    if hashPriv != expectedHashPriv:
        raise Exception(str(hashPriv) + ' != ' + str(expectedHashPriv))
    (r2, s2) = signHashWithK(H, pub, priv, k)
    if r2 != r:
        raise Exception(str(r2) + ' != ' + str(r))
    if s2 != s:
        raise Exception(str(s2) + ' != ' + str(s))
    print(k, priv)
