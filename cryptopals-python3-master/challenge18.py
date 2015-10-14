import base64
import struct
from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor

class CTR:
    def __init__(self, ECB, nonce):
        self._ECB = ECB
        self._nonce = nonce
        self._blocksize = 16
        self._keybytes = b''
        self._blockcount = 0

    def encrypt(self, plaintext):
        # Work around strxor() not handling zero-length strings
        # gracefully.
        if len(plaintext) == 0:
            return b''

        keystream = self._keybytes
        while len(keystream) < len(plaintext):
            keyblock = self._ECB.encrypt(struct.pack('<QQ', self._nonce, self._blockcount))
            keystream += keyblock
            self._blockcount += 1

        if len(keystream) > len(plaintext):
            self._keybytes = keystream[len(plaintext):]
            keystream = keystream[:len(plaintext)]

        return strxor(plaintext, keystream)

    def decrypt(self, ciphertext):
        return self.encrypt(ciphertext)

if __name__ == '__main__':
    x = base64.b64decode('L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==')

    key = b'YELLOW SUBMARINE'
    cipher1 = CTR(AES.new(key, AES.MODE_ECB), 0)
    y = cipher1.decrypt(x)
    print(y)
    cipher2 = CTR(AES.new(key, AES.MODE_ECB), 0)
    z = cipher2.encrypt(y)
    if x != z:
        raise Exception(x + b' != ' + z)
