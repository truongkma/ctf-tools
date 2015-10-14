from Crypto.Random import random
import binascii
import hashlib
import challenge39

decryptedHashes = set()

pub, priv = challenge39.genKey(128)

def encrypt(plaintext):
    return challenge39.encryptbytes(pub, plaintext)

def decryptOnce(ciphertext):
    sha1 = hashlib.sha1()
    sha1.update(ciphertext)
    digest = sha1.digest()
    if digest in decryptedHashes:
        raise ValueError('Already decrypted')
    decryptedHashes.add(digest)
    return challenge39.decryptbytes(priv, ciphertext)

if __name__ == '__main__':
    plaintext = b'secret text'
    ciphertext = encrypt(plaintext)
    plaintext2 = decryptOnce(ciphertext)
    if plaintext2 != plaintext:
        raise ValueError(plaintext2 + b' != ' + plaintext)

    (e, n) = pub
    s = random.randint(2, n - 1)
    c = challenge39.bytestonum(ciphertext)
    c2 = (pow(s, e, n) * c) % n
    ciphertext2 = challenge39.numtobytes(c2)
    plaintext3 = decryptOnce(ciphertext2)
    p3 = challenge39.bytestonum(plaintext3)
    p4 = (p3 * challenge39.invmod(s, n)) % n
    plaintext4 = challenge39.numtobytes(p4)

    if plaintext4 != plaintext:
        raise ValueError(plaintext4 + b' != ' + plaintext)
