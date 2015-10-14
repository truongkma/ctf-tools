import challenge39
import challenge47
import itertools
import re

pub, priv = challenge39.genKey(768)

def parityOracle(c):
    _, n = pub
    k = (n.bit_length() + 7) // 8
    p = challenge39.decryptnum(priv, c)
    pbytes = challenge39.numtobytes(p)
    pbytes = (b'\x00' * (k - len(pbytes))) + pbytes
    return pbytes[0:2] == b'\x00\x02'

def computeNextS(e, n, M, s, B, c0):
    if len(M) > 1:
        while True:
            s += 1
            c = (c0 * pow(s, e, n)) % n
            if parityOracle(c):
                return (s, c)
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
    if len(M) == 0:
        raise Exception('unexpected1')
    Mnew = []
    for a, b in M:
        minR = (a * s - 3 * B + 1 + n - 1) // n
        maxR = (b * s - 2 * B) // n
        for r in range(minR, maxR + 1):
            ai = max(a, (2*B + r*n + s - 1) // s)
            bi = min(b, (3*B - 1 + r*n) // s)
            if ai > bi:
                continue
            Mnew += [(ai, bi)]
    if len(Mnew) == 0:
        raise Exception('unexpected')
    return Mnew

def deducePlaintext(ciphertext, pub, parityOracle):
    e, n = pub
    k = (n.bit_length() + 7) // 8
    B = 2**(8*(k-2))
    c0 = challenge39.bytestonum(ciphertext)
    M = [(2*B, 3*B - 1)]
    (s, c) = challenge47.computeFirstS(e, n, B, c0, parityOracle)
    M = getNextInterval(n, M, s, B)
    while True:
        if len(M) == 1 and M[0][0] == M[0][1]:
            m = M[0][0]
            return b'\x00' + challenge39.numtobytes(m)
        (s, c) = computeNextS(e, n, M, s, B, c0)
        M = getNextInterval(n, M, s, B)

if __name__ == '__main__':
    _, n = pub
    plaintext = challenge47.padPKCS15(b'kick it, CC', n)
    ciphertext = challenge39.encryptbytes(pub, plaintext)
    plaintext2 = deducePlaintext(ciphertext, pub, parityOracle)
    if plaintext2 != plaintext:
        raise Exception(plaintext2 + b' != ' + plaintext)
