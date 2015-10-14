from Crypto.Cipher import Blowfish
import struct
import util

def MerkleDamgard(f, processIV, blockLength, padMessage):
    def hashFn(m, iv, pad=True):
        H = processIV(iv)
        if pad:
            m = padMessage(m, len(m))
        elif len(m) % blockLength != 0:
            raise Exception('message of length {0} not a multiple of block length {1}'.format(len(m), blockLength))
        for block in (m[x:x+blockLength] for x in range(0, len(m), blockLength)):
            H = f(block, H)
        return H
    return hashFn

badHashHashLength = 2

def badHashF(messageBlock, state):
    cipher = Blowfish.new(state, Blowfish.MODE_ECB)
    newState = cipher.encrypt(messageBlock)[:badHashHashLength]
    return newState

def badHashProcessIV(iv):
    if len(iv) < badHashHashLength:
        return iv + (b'\x00' * (badHashHashLength - len(iv)))
    else:
        return iv[:badHashHashLength]

badHashBlockLength = 8

def badHashPadMessage(m, l):
    m += b'\x80'
    m += b'\x00' * ((-4 - (len(m) % badHashBlockLength)) % badHashBlockLength)
    m += struct.pack('>I', l)
    return m

badHash = MerkleDamgard(badHashF, badHashProcessIV, badHashBlockLength, badHashPadMessage)

def findPrefixCollisionFromIter(hashFn, iv, inputIter):
    hashToString = {}
    for s in inputIter:
        h = hashFn(s, iv, pad=False)
        if h in hashToString:
            return (h, s, hashToString[h])
        else:
            hashToString[h] = s
    return None, None, None

def findPrefixCollision(hashFn, iv, blockLength, hashLength):
    state, s1, s2 = findPrefixCollisionFromIter(hashFn, iv, (i.to_bytes(blockLength, byteorder='little') for i in range(2**(hashLength*8))))
    if state is None:
        raise Error('unexpected')
    return state, s1, s2

def extendCollisions(hashFn, state, blockLength, hashLength, collisions):
    state, s1, s2 = findPrefixCollision(hashFn, state, blockLength, hashLength)
    return state, [x + s for x in collisions for s in [s1, s2]]

def generateCollisions(hashFn, iv, blockLength, hashLength, n):
    state, s1, s2 = findPrefixCollision(hashFn, iv, blockLength, hashLength)
    collisions = [s1, s2]
    for i in range(n-1):
        state, collisions = extendCollisions(hashFn, state, blockLength, hashLength, collisions)
    return state, collisions

lessBadHashHashLength = 3

def lessBadHashF(messageBlock, state):
    cipher = Blowfish.new(state, Blowfish.MODE_ECB)
    newState = cipher.encrypt(messageBlock)[:lessBadHashHashLength]
    return newState

lessBadHashProcessIV = badHashProcessIV
lessBadHashBlockLength = badHashBlockLength
lessBadHashPadMessage = badHashPadMessage

lessBadHash = MerkleDamgard(lessBadHashF, lessBadHashProcessIV, lessBadHashBlockLength, lessBadHashPadMessage)

# hashFn is assumed to be the cheap one.
def findCollision2(hashFn, iv, blockLength, hashLength, hashFn2, iv2, blockLength2, hashLength2):
    state, collisions = generateCollisions(hashFn, iv, blockLength, hashLength, hashLength2*4)
    while True:
        _, s1, s2 = findPrefixCollisionFromIter(hashFn2, iv2, collisions)
        if s1 is not None:
            return s1, s2
        state, collisions = extendCollisions(hashFn, state, blockLength, hashLength, collisions)

if __name__ == '__main__':
    _, collisions = generateCollisions(badHash, b'', badHashBlockLength, badHashHashLength, 5)
    for s in collisions:
        print(s, badHash(s, b''))

    s1, s2 = findCollision2(badHash, b'', badHashBlockLength, badHashHashLength, lessBadHash, b'', lessBadHashBlockLength, lessBadHashHashLength)
    print(s1, s2, badHash(s1, b''), badHash(s2, b''), lessBadHash(s1, b''), lessBadHash(s2, b''))
