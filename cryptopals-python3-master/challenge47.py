from Crypto.Random import random
import challenge39
import re

pub, priv = challenge39.genKey(256)

def parityOracle(c):
    _, n = pub
    k = (n.bit_length() + 7) // 8
    p = challenge39.decryptnum(priv, c)
    pbytes = challenge39.numtobytes(p)
    pbytes = (b'\x00' * (k - len(pbytes))) + pbytes
    return pbytes[0:2] == b'\x00\x02'

def randnonzerobytes(k):
    return bytes(random.sample(range(1, 256), k))

def padPKCS15(s, n):
    if len(s) < 8:
        raise Exception('unexpected')
    k = (n.bit_length() + 7) // 8
    padding = randnonzerobytes(k - 3 - len(s))
    return b'\x00\x02' + padding + b'\x00' + s

def computeFirstS(e, n, B, c0, parityOracle):
    s = (n + 3*B - 1) // (3*B)
    while True:
        c = (c0 * pow(s, e, n)) % n
        if parityOracle(c):
            return (s, c)
        s += 1

def computeNextS(e, n, M, s, B, c0):
    if len(M) > 1:
        raise Exception('unexpected')
    else:
        a, b = M[0]
        r = (2 * (b * s - 2 * B) + n - 1) // n
        while True:
            sLow = (2*B + r*n + b - 1) // b
            sHigh = (3*B + r*n + a - 1) // a
            for s in range(sLow, sHigh):
                c = (c0 * pow(s, e, n)) % n
                if parityOracle(c):
                    return (s, c)
            r += 1

def getNextInterval(n, M, s, B):
    if len(M) > 1:
        raise Exception('unexpected')
    a, b = M[0]
    minR = (a * s - 3 * B + 1 + n - 1) // n
    maxR = (b * s - 2 * B) // n
    if maxR > minR:
        raise Exception('unexpected')
    r = minR
    ai = max(a, (2*B + r*n + s - 1) // s)
    bi = min(b, (3*B - 1 + r*n) // s)
    if ai > bi:
        raise Exception('unexpected')
    return [(ai, bi)]

def deducePlaintext(ciphertext, pub, parityOracle):
    e, n = pub
    k = (n.bit_length() + 7) // 8
    B = 2**(8*(k-2))
    c0 = challenge39.bytestonum(ciphertext)
    M = [(2*B, 3*B - 1)]
    (s, c) = computeFirstS(e, n, B, c0, parityOracle)
    M = getNextInterval(n, M, s, B)
    while True:
        if len(M) == 1 and M[0][0] == M[0][1]:
            m = M[0][0]
            return b'\x00' + challenge39.numtobytes(m)
        (s, c) = computeNextS(e, n, M, s, B, c0)
        M = getNextInterval(n, M, s, B)

if __name__ == '__main__':
    _, n = pub
    plaintext = padPKCS15(b'kick it, CC', n)
    ciphertext = challenge39.encryptbytes(pub, plaintext)
    plaintext2 = deducePlaintext(ciphertext, pub, parityOracle)
    if plaintext2 != plaintext:
        raise Exception(plaintext2 + b' != ' + plaintext)
