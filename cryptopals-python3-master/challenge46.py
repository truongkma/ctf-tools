import base64
import challenge39

pub, priv = challenge39.genKey(1024)

def parityOracle(c):
    p = challenge39.decryptnum(priv, c)
    return p % 2

def deducePlaintext(ciphertext, pub, parityOracle):
    (e, n) = pub
    low = 0
    high = 1
    denom = 1
    c = challenge39.bytestonum(ciphertext)
    k = pow(2, e, n)
    for _ in range(n.bit_length()):
        c  = (c * k) % n
        p = parityOracle(c)
        d = high - low
        low *= 2
        high *= 2
        denom *= 2
        if p == 0:
            high -= d
        else:
            low += d
        hightext = challenge39.numtobytes(n * high // denom)
        print(hightext)
    return hightext

if __name__ == '__main__':
    encodedPlaintext = b'VGhhdCdzIHdoeSBJIGZvdW5kIHlvdSBkb24ndCBwbGF5IGFyb3VuZCB3aXRoIHRoZSBGdW5reSBDb2xkIE1lZGluYQ=='
    plaintext = base64.b64decode(encodedPlaintext)
    ciphertext = challenge39.encryptbytes(pub, plaintext)
    plaintext2 = deducePlaintext(ciphertext, pub, parityOracle)
    if plaintext2 != plaintext:
        raise Exception(b'Invalid plaintext ' + plaintext2)
