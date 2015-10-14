from Crypto.Random import random
import challenge21

def getMSB(x, n):
    if n < 0:
        return 0
    return (x >> (31 - n)) & 1

def setMSB(x, n, b):
    return x | (b << (31 - n))

def undoRightShiftXor(y, s):
    z = 0
    for i in range(32):
        z = setMSB(z, i, getMSB(y, i) ^ getMSB(z, i - s))
    return z

def getLSB(x, n):
    if n < 0:
        return 0
    return (x >> n) & 1

def setLSB(x, n, b):
    return x | (b << n)

def undoLeftShiftXorAnd(y, s, k):
    z = 0
    for i in range(32):
       z = setLSB(z, i, getLSB(y, i) ^ (getLSB(z, i - s) & getLSB(k, i)))
    return z

def untemper(y):
    y = undoRightShiftXor(y, 18)
    y = undoLeftShiftXorAnd(y, 15, 0xefc60000)
    y = undoLeftShiftXorAnd(y, 7, 0x9d2c5680)
    y = undoRightShiftXor(y, 11)
    return y

seed = random.getrandbits(32)
rng = challenge21.MT19937(seed)
MT = [0] * 624
for i in range(624):
    MT[i] = untemper(rng.uint32())
rng2 = challenge21.MT19937(0)
rng2._MT = MT

for i in range(1000):
    a = rng.uint32()
    b = rng2.uint32()
    if a != b:
        raise Exception(str(i) + ' ' + str(a) + ' != ' + str(b))
