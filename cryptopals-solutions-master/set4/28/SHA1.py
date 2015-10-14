#! /usr/bin/env python

################################################################################
# The following code is a minor modification of code taken from                #
#                                       https://github.com/pcaro90/Python-SHA1 #
################################################################################

# ----------------------------------------------------------------------
# Copyright (c) 2014 Pablo Caro. All Rights Reserved.
# Pablo Caro <me@pcaro.es> - https://pcaro.es/
# SHA1.py
# ----------------------------------------------------------------------

import sys


class __SHA1:
    def __init__(self):
        self.__H = [
            0x67452301,
            0xEFCDAB89,
            0x98BADCFE,
            0x10325476,
            0xC3D2E1F0
            ]

    def __str__(self):
        return ''.join((hex(h)[2:]).rjust(8, '0') for h in self.__H)

    # Private static methods used for internal operations.
    @staticmethod
    def __ROTL(n, x, w=32):
        return ((x << n) | (x >> w - n))

    @staticmethod
    def __padding(stream):
        l = len(stream)  # Bytes
        hl = [int((hex(l*8)[2:]).rjust(16, '0')[i:i+2], 16)
              for i in range(0, 16, 2)]

        l0 = (56 - l) % 64
        if not l0:
            l0 = 64

        if isinstance(stream, str):
            stream += chr(0b10000000)
            stream += chr(0)*(l0-1)
            for a in hl:
                stream += chr(a)
        elif isinstance(stream, bytes):
            stream += bytes([0b10000000])
            stream += bytes(l0-1)
            stream += bytes(hl)

        return stream

    @staticmethod
    def __prepare(stream):
        M = []
        n_blocks = len(stream) // 64

        stream = bytearray(stream)

        for i in range(n_blocks):  # 64 Bytes per Block
            m = []

            for j in range(16):  # 16 Words per Block
                n = 0
                for k in range(4):  # 4 Bytes per Word
                    n <<= 8
                    n += stream[i*64 + j*4 + k]

                m.append(n)

            M.append(m[:])

        return M

    @staticmethod
    def __debug_print(t, a, b, c, d, e):
        print('t = {0} : \t'.format(t),
              (hex(a)[2:]).rjust(8, '0'),
              (hex(b)[2:]).rjust(8, '0'),
              (hex(c)[2:]).rjust(8, '0'),
              (hex(d)[2:]).rjust(8, '0'),
              (hex(e)[2:]).rjust(8, '0')
              )

    # Private instance methods used for internal operations.
    def __process_block(self, block):
        MASK = 2**32-1

        W = block[:]
        for t in range(16, 80):
            W.append(self.__ROTL(1, (W[t-3] ^ W[t-8] ^ W[t-14] ^ W[t-16]))
                     & MASK)

        a, b, c, d, e = self.__H[:]

        for t in range(80):
            if t <= 19:
                K = 0x5a827999
                f = (b & c) ^ (~b & d)
            elif t <= 39:
                K = 0x6ed9eba1
                f = b ^ c ^ d
            elif t <= 59:
                K = 0x8f1bbcdc
                f = (b & c) ^ (b & d) ^ (c & d)
            else:
                K = 0xca62c1d6
                f = b ^ c ^ d

            T = ((self.__ROTL(5, a) + f + e + K + W[t]) & MASK)
            e = d
            d = c
            c = self.__ROTL(30, b) & MASK
            b = a
            a = T

            #SHA1.debug_print(t, a,b,c,d,e)

        self.__H[0] = (a + self.__H[0]) & MASK
        self.__H[1] = (b + self.__H[1]) & MASK
        self.__H[2] = (c + self.__H[2]) & MASK
        self.__H[3] = (d + self.__H[3]) & MASK
        self.__H[4] = (e + self.__H[4]) & MASK

    # Public methods for class use.
    def update(self, stream):
        stream = self.__padding(stream)
        stream = self.__prepare(stream)

        for block in stream:
            self.__process_block(block)

    def digest(self):
        pass

    def hexdigest(self):
        s = ''
        for h in self.__H:
            s += (hex(h)[2:]).rjust(8, '0')
        return s


def SHA1_hexdigest(content):
    h = __SHA1()
    h.update(content)
    hex_sha = h.hexdigest()
    return hex_sha

def usage():
    print('Usage: python SHA1.py <file> [<file> ...]')
    sys.exit()


def main():

    if len(sys.argv) < 2:
        usage()

    for filename in sys.argv[1:]:
        try:
            with open(filename, 'rb') as f:
                content = f.read()

        except:
            print ('ERROR: Input file "{0}" cannot be read.'.format(filename))

        else:
            print("{0}  {1}".format(SHA1_hexdigest(content), filename))


if __name__ == '__main__':
    main()
