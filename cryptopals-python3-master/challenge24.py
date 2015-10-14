from Crypto.Util.strxor import strxor
from Crypto.Random import random
import challenge21
import struct
import time
import util

class MT19937Cipher:
    def __init__(self, key):
        self._rng = challenge21.MT19937(key & 0xffff)
        self._keybytes = b''

    def encrypt(self, plaintext):
        # Work around strxor() not handling zero-length strings
        # gracefully.
        if len(plaintext) == 0:
            return b''

        keystream = self._keybytes
        while len(keystream) < len(plaintext):
            keyblock = struct.pack('<L', self._rng.uint32())
            keystream += keyblock

        if len(keystream) > len(plaintext):
            self._keybytes = keystream[len(plaintext):]
            keystream = keystream[:len(plaintext)]

        return strxor(plaintext, keystream)

    def decrypt(self, ciphertext):
        return self.encrypt(ciphertext)

key = random.getrandbits(16)

def encryption_oracle(plaintext):
    prefix = util.randbytes(random.randint(4, 20))
    cipher = MT19937Cipher(key)
    return cipher.encrypt(prefix + plaintext)

def recover_key(encryption_oracle):
    plaintext = b'0' * 14
    ciphertext = encryption_oracle(plaintext)
    prefix_len = len(ciphertext) - len(plaintext)
    for i in range(2**16-1):
        cipher = MT19937Cipher(i)
        s = cipher.encrypt(b'0' * len(ciphertext))
        if ciphertext[prefix_len:] == s[prefix_len:]:
            return i
    raise Exception('unexpected')

print(key, recover_key(encryption_oracle))

def token_oracle():
    seed = int(time.time())
    cipher = MT19937Cipher(seed)
    plaintext = b'0' * random.randint(4, 20)
    return cipher.encrypt(plaintext)

def is_token_for_current_time(token):
    seed = int(time.time())
    cipher = MT19937Cipher(seed)
    plaintext = b'0' * len(token)
    return cipher.encrypt(plaintext) == token

x = token_oracle()
print(x, is_token_for_current_time(x))
