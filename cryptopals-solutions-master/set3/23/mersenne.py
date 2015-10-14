#! /usr/bin/env python


class MT19937():
    """
    An implementation of the MT19937 algorithm for
    pseudo random number generation
    """

    def __init__(self, seed):
        """
        Initialize generator from a seed
        """
        if type(seed) == int:
            self.index = 0
            self.MT = [0]*624
            self.MT[0] = seed
            for i in range(1, 624):
                self.MT[i] = (2**32-1) & \
                    (0x6c078965 * (self.MT[i-1] ^ (self.MT[i-1] >> 30)) + i)
        elif type(seed) == list and len(seed) == 624:
            self.index = 0
            self.MT = seed[:]
        else:
            raise Exception

    def random(self):
        return self.extract_number()

    @staticmethod
    def temper(value):
        y = value
        y = y ^ (y >> 11)
        y = y ^ ((y << 7) & 0x9d2c5680)
        y = y ^ ((y << 15) & 0xefc60000)
        y = y ^ (y >> 18)
        return y

    @staticmethod
    def untemper(value):
        assert(value < 2**32)
        assert(value >= 0)

        y = value

        # Inverse of y = y ^ (y >> 18)
        y = y ^ (y >> 18)

        # Inverse of y = y ^ ((y << 15) & 0xefc60000)
        y = y ^ ((y & 0x1df8c) << 15)

        # Inverse of y = y ^ ((y << 7) & 0x9d2c5680)
        t = y
        t = ((t & 0x0000002d) << 7) ^ y
        t = ((t & 0x000018ad) << 7) ^ y
        t = ((t & 0x001a58ad) << 7) ^ y
        y = ((t & 0x013a58ad) << 7) ^ y

        # Inverse of y = y ^ (y >> 11)
        top = y & 0xffe00000
        mid = y & 0x001ffc00
        low = y & 0x000003ff

        y = top | ((top >> 11) ^ mid) | ((((top >> 11) ^ mid) >> 11) ^ low)

        return y

    @staticmethod
    def generate_clone(values):
        if type(values) != list:
            raise Exception
        if len(values) < 624:
            raise Exception
        values = values[:624]
        ret = MT19937([MT19937.untemper(v) for v in values])
        return ret

    def extract_number(self):
        """
        Extract a tempered pseudorandom number based on the index-th value
        Call generate_numbers every 624 numbers
        """
        if self.index == 0:
            self.generate_numbers()

        y = MT19937.temper(self.MT[self.index])

        self.index = (self.index + 1) % 624

        return y

    def generate_numbers(self):
        """
        Generate an array of 624 untempered numbers
        """
        for i in range(624):
            y = (self.MT[i] & 0x80000000) + (self.MT[(i+1) % 624] & 0x7fffffff)

            self.MT[i] = self.MT[(i+397) % 624] ^ (y >> 1)

            if y % 2 != 0:
                self.MT[i] = self.MT[i] ^ 0x9908b0df

if __name__ == '__main__':
    m = MT19937(0)
    n = MT19937(0)
    if [m.random() for __ in range(700)] == [n.random() for __ in range(700)]:
        print "[+] Mersenne same seed test passed"
    else:
        print "[-] Mersenne same seed test failed"

    m = MT19937(0)
    n = MT19937(1)
    if [m.random() for __ in range(700)] != [n.random() for __ in range(700)]:
        print "[+] Mersenne different seed test passed"
    else:
        print "[-] Mersenne different seed test failed"

    for i in range(10):
        r = m.random()
        if MT19937.untemper(MT19937.temper(r)) == r:
            print "[+] untemper(temper(r))==r test passed. r = %d" % r
        else:
            print "[-] untemper(temper(r))==r test failed. r = %d" % r

