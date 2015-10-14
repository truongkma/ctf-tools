import base64
from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor

class CBC:
    def __init__(self, ECB, IV):
        self._ECB = ECB
        self._IV = IV
        self._blocksize = 16

    def _getBlocks(self, s):
        return [s[i:i+self._blocksize] for i in range(0, len(s), self._blocksize)]

    def encrypt(self, plaintext):
        plainblocks = self._getBlocks(plaintext)
        ciphertext = b''
        prev = self._IV
        for i in range(len(plainblocks)):
            plainblock = plainblocks[i]
            cipherblock = self._ECB.encrypt(strxor(plainblock, prev))
            ciphertext += cipherblock
            prev = cipherblock
        return ciphertext

    def decrypt(self, ciphertext):
        cipherblocks = self._getBlocks(ciphertext)
        plaintext = b''
        prev = self._IV
        for i in range(len(cipherblocks)):
            cipherblock = cipherblocks[i]
            plainblock = strxor(self._ECB.decrypt(cipherblock), prev)
            plaintext += plainblock
            prev = cipherblock
        return plaintext

if __name__ == '__main__':
    x = base64.b64decode(open('10.txt', 'r').read())

    key = b'YELLOW SUBMARINE'
    cipher = CBC(AES.new(key, AES.MODE_ECB), bytes([0] * 16))
    y = cipher.decrypt(x)
    print(y)
    z = cipher.encrypt(y)
    if x != z:
        raise Exception(x + b' != ' + z)
