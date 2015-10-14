# Taken from https://github.com/sfstpala/SlowSHA
class SHA1 (object):
    _default_h0, _default_h1, _default_h2, _default_h3, _default_h4, = (
        0x67452301, 0xefcdab89, 0x98badcfe, 0x10325476, 0xc3d2e1f0)

    def __init__(self, message, h0 = _default_h0, h1 = _default_h1, h2 = _default_h2, h3 = _default_h3, h4 = _default_h4, length = None):
        self._h0 = h0
        self._h1 = h1
        self._h2 = h2
        self._h3 = h3
        self._h4 = h4
        if length is None:
            length = len(message) * 8
        length = bin(length)[2:].rjust(64, "0")
        while len(message) > 64:
            self._handle(''.join(bin(i)[2:].rjust(8, "0")
                for i in message[:64]))
            message = message[64:]
        message = ''.join(bin(i)[2:].rjust(8, "0") for i in message) + "1"
        message += "0" * ((448 - len(message) % 512) % 512) + length
        for i in range(len(message) // 512):
            self._handle(message[i * 512:i * 512 + 512])


    def _handle(self, chunk):

        lrot = lambda x, n: (x << n) | (x >> (32 - n))
        w = []

        for j in range(len(chunk) // 32):
            w.append(int(chunk[j * 32:j * 32 + 32], 2))

        for i in range(16, 80):
            w.append(lrot(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1)
                & 0xffffffff)

        a = self._h0
        b = self._h1
        c = self._h2
        d = self._h3
        e = self._h4

        for i in range(80):

            if i <= i <= 19:
                f, k = d ^ (b & (c ^ d)), 0x5a827999
            elif 20 <= i <= 39:
                f, k = b ^ c ^ d, 0x6ed9eba1
            elif 40 <= i <= 59:
                f, k = (b & c) | (d & (b | c)), 0x8f1bbcdc
            elif 60 <= i <= 79:
                f, k = b ^ c ^ d, 0xca62c1d6

            temp = lrot(a, 5) + f + e + k + w[i] & 0xffffffff
            a, b, c, d, e = temp, a, lrot(b, 30), c, d

        self._h0 = (self._h0 + a) & 0xffffffff
        self._h1 = (self._h1 + b) & 0xffffffff
        self._h2 = (self._h2 + c) & 0xffffffff
        self._h3 = (self._h3 + d) & 0xffffffff
        self._h4 = (self._h4 + e) & 0xffffffff

    def _digest(self):
        return (self._h0, self._h1, self._h2, self._h3, self._h4)

    def hexdigest(self):
        return ''.join(hex(i)[2:].rjust(8, "0")
            for i in self._digest())

    def digest(self):
        hexdigest = self.hexdigest()
        return bytes(int(hexdigest[i * 2:i * 2 + 2], 16)
            for i in range(len(hexdigest) // 2))

def authSHA1(key, message):
    return SHA1(key + message).digest()
