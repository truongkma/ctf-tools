from Crypto.Random import random
import challenge28
import md4
import struct
import util

def authMD4(key, message):
    md4obj = md4.md4()
    md4obj.update(key + message)
    return md4obj.digest()

def padMD4(s):
    l = len(s) * 8
    s += b'\x80'
    s += b'\x00' * ((56 - (len(s) % 64)) % 64)
    s += struct.pack("<2I", l & 0xffffffff, (l>>32) & 0xffffffff)
    return s

keylen = random.randint(0, 100)
key = util.randbytes(keylen)

def validate(message, digest):
    return authMD4(key, message) == digest

message = b'comment1=cooking%20MCs;userdata=foo;comment2=%20like%20a%20pound%20of%20bacon'
messageDigest = authMD4(key, message)

def forgeHash(keylen, message, digest, suffix):
    paddedForgedMessageWithKey = padMD4(key + message) + suffix
    forgedMessage = paddedForgedMessageWithKey[keylen:]
    h = struct.unpack('<4I', digest)
    md4obj = md4.md4(h[0], h[1], h[2], h[3])
    md4obj.update(suffix)
    forgedDigest = md4obj.digest(len(paddedForgedMessageWithKey) * 8)
    return (forgedMessage, forgedDigest)

def forgeValidatingHash(maxkeylen, message, digest, suffix):
    for i in range(maxkeylen):
        (forgedMessage, forgedDigest) = forgeHash(i, message, digest, suffix)
        if validate(forgedMessage, forgedDigest):
            return(forgedMessage, forgedDigest)
    raise Exception('unexpected')

print(forgeValidatingHash(100, message, messageDigest, b';admin=true'))
