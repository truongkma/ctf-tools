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
        self.index = 0
        self.MT = [0]*624
        self.MT[0] = seed
        for i in range(1, 624):
            self.MT[i] = (2**32-1) & \
                (0x6c078965 * (self.MT[i-1] ^ (self.MT[i-1] >> 30)) + i)

    def random(self):
        return self.extract_number()

    def extract_number(self):
        """
        Extract a tempered pseudorandom number based on the index-th value
        Call generate_numbers every 624 numbers
        """
        if self.index == 0:
            self.generate_numbers()

        y = self.MT[self.index]
        y = y ^ (y >> 11)
        y = y ^ ((y << 7) & 0x9d2c5680)
        y = y ^ ((y << 15) & 0xefc60000)
        y = y ^ (y >> 18)

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
        print "Mersenne same seed test passed"
    else:
        print "Mersenne same seed test failed"

    m = MT19937(0)
    n = MT19937(1)
    if [m.random() for __ in range(700)] != [n.random() for __ in range(700)]:
        print "Mersenne different seed test passed"
    else:
        print "Mersenne different seed test failed"
