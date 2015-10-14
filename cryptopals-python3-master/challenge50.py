from Crypto.Util.strxor import strxor
import binascii
import challenge49
import itertools
import string
import util

def insecureHash(s):
    return challenge49.CBC_MAC(b'YELLOW SUBMARINE', b'\x00' * 16, s)

def prependAndCollide(s, prefix):
    prefixHash = insecureHash(prefix)
    paddedPrefix = util.padPKCS7(prefix, 16)
    return paddedPrefix + strxor(s[:16], prefixHash) + s[16:]

def prependAndCollidePrintable(s, prefix):
    # Ensure that the padding character is \t (== 0x09).
    numFreeBytes = (7 - len(prefix)) % 16
    if numFreeBytes == 0:
        numFreeBytes = 16
    for freeBytes in itertools.product(range(32, 127), repeat=numFreeBytes):
        paddedPrefix = prefix + bytes(freeBytes)
        collision = prependAndCollide(s, paddedPrefix)
        scrambledBytes = collision[-len(s):-len(s) + 16]
        if all(c >= 32 and c < 127 for c in scrambledBytes):
            return collision

s = b"alert('MZA who was that?');\n"
sHash = insecureHash(s)
print(binascii.hexlify(sHash))

prefix = b"alert('Ayo, the Wu is back!'); //"
collision = prependAndCollidePrintable(s, prefix)
print(collision, binascii.hexlify(insecureHash(collision)))
