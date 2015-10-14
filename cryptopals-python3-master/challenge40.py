import challenge39
import binascii
import math

(pub0, priv0) = challenge39.genKey(256)
(pub1, priv1) = challenge39.genKey(256)
(pub2, priv2) = challenge39.genKey(256)

plaintext = b'This is a plaintext string'
plainnum = challenge39.bytestonum(plaintext)

c0 = challenge39.encryptnum(pub0, plainnum)
c1 = challenge39.encryptnum(pub1, plainnum)
c2 = challenge39.encryptnum(pub2, plainnum)

n0 = pub0[1]
n1 = pub1[1]
n2 = pub2[1]

ms0 = n1 * n2
ms1 = n0 * n2
ms2 = n0 * n1

N = n0 * n1 * n2

r0 = (c0 * ms0 * challenge39.invmod(ms0, n0))
r1 = (c1 * ms1 * challenge39.invmod(ms1, n1))
r2 = (c2 * ms2 * challenge39.invmod(ms2, n2))

r = (r0 + r1 + r2) % N

def floorRoot(n, s):
    b = n.bit_length()
    p = math.ceil(b/s)
    x = 2**p
    while x > 1:
        y = (((s - 1) * x) + (n // (x**(s-1)))) // s
        if y >= x:
            return x
        x = y
    return 1

if __name__ == '__main__':
    m = floorRoot(r, 3)
    mstr = challenge39.numtobytes(m)

    if mstr != plaintext:
        raise Exception(mstr + b' != ' + plaintext)
