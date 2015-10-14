from Crypto.Cipher import AES
from Crypto.Random import random
import base64
import challenge10
import challenge15
import util

strings = [
    b'MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=',
    b'MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=',
    b'MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==',
    b'MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==',
    b'MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl',
    b'MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==',
    b'MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==',
    b'MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=',
    b'MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=',
    b'MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93'
]

key = util.randbytes(16)

def ciphertext_oracle():
    s = base64.b64decode(random.choice(strings))
    iv = util.randbytes(16)
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), iv)
    return (iv, cipher.encrypt(util.padPKCS7(s, 16)))

def padding_oracle(iv, s):
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), iv)
    paddedT = cipher.decrypt(s)
    try:
        t = challenge15.unpadPKCS7(paddedT)
    except ValueError:
        return False
    return True

def decipher_last_block_previous_byte(iv, s, padding_oracle, knownI, knownP):
    k = len(knownI) + 1
    prefix = util.randbytes(16 - k)
    for i in range(256):
        c1 = s[-32:-16] if len(s) > 16 else iv
        c1p = prefix + bytes([i]) + bytes([ch ^ k for ch in knownI])
        sp = s[:-32] + c1p + s[-16:]
        if padding_oracle(iv, sp):
            iPrev = i ^ k
            pPrev = c1[-k] ^ iPrev
            return (bytes([iPrev] + list(knownI)), bytes([pPrev] + list(knownP)))
    raise Exception('unexpected')

def decipher_last_block(iv, s, padding_oracle):
    knownI = b''
    knownP = b''
    for i in range(16):
        (knownI, knownP) = decipher_last_block_previous_byte(iv, s, padding_oracle, knownI, knownP)
    return knownP

def decipher(iv, s, padding_oracle):
    knownP = b''
    for i in range(len(s) // 16):
        st = s if i == 0 else s[:-i * 16]
        knownP = decipher_last_block(iv, st, padding_oracle) + knownP
    return challenge15.unpadPKCS7(knownP)

(iv, s) = ciphertext_oracle()
print(decipher(iv, s, padding_oracle))
