from Crypto.Util.strxor import strxor
import base64
import challenge3
import challenge19
import itertools

strings = [base64.b64decode(x) for x in open('20.txt', 'r').read().split('\n')]
strings = strings[:-1]

encryptedStrings = [challenge19.encryptString(s) for s in strings]

def breakSameKey(strings):
    transposedStrings = list(zip(*strings))
    key = [challenge3.breakSingleByteXOR(bytes(x))[0] for x in transposedStrings]
    return bytes(key)

key = breakSameKey(encryptedStrings)
key = bytes([encryptedStrings[0][0] ^ ord('I')]) + key[1:]
key = challenge19.extendKey(key, encryptedStrings[13], b'-M ')
key = challenge19.extendKey(key, encryptedStrings[16], b'ime ')
key = challenge19.extendKey(key, encryptedStrings[1], b'htnin')
key = challenge19.extendKey(key, encryptedStrings[2], b'y')
key = challenge19.extendKey(key, encryptedStrings[6], b'ty')
key = challenge19.extendKey(key, encryptedStrings[0], b'i')
key = challenge19.extendKey(key, encryptedStrings[3], b'n up')
key = challenge19.extendKey(key, encryptedStrings[7], b'ession')
key = challenge19.extendKey(key, encryptedStrings[4], b'or ')
key = challenge19.extendKey(key, encryptedStrings[1], b'ghtenin')
key = challenge19.extendKey(key, encryptedStrings[17], b'able')
key = challenge19.extendKey(key, encryptedStrings[11], b'st')
key = challenge19.extendKey(key, encryptedStrings[2], b'k')
key = challenge19.extendKey(key, encryptedStrings[12], b'nk')
key = challenge19.extendKey(key, encryptedStrings[26], b've ')
key = challenge19.extendKey(key, encryptedStrings[41], b'll')
key = challenge19.extendKey(key, encryptedStrings[21], b'ace')
key = challenge19.extendKey(key, encryptedStrings[26], b'hole scenery')
kl = len(key)
for i in range(len(encryptedStrings)):
    s = encryptedStrings[i]
    decrypted = strxor(s[:kl], key[:len(s)]) + s[kl:]
    if decrypted != strings[i]:
        raise Exception('Invalid decryption')
    print(i, decrypted)
