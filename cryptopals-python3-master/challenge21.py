class MT19937:
    def __init__(self, seed):
        self._index = 0
        self._MT = [0] * 624
        self._MT[0] = seed & 0xffffffff
        for i in range(1, 624):
            self._MT[i] = ((0x6c078965 * (self._MT[i-1] ^ (self._MT[i-1] >> 30))) + i) & 0xffffffff

    def uint32(self):
        if self._index == 0:
            self.generate_numbers()

        y = self._MT[self._index]
        y ^= (y >> 11)
        y ^= ((y << 7) & 0x9d2c5680)
        y ^= ((y << 15) & 0xefc60000)
        y ^= (y >> 18)

        self._index = (self._index + 1) % 624
        return y

    def generate_numbers(self):
        for i in range(624):
            y = (self._MT[i] & 0x80000000) + (self._MT[(i+1) % 624] & 0x7fffffff)
            self._MT[i] = self._MT[(i + 397) % 624] ^ (y >> 1)
            if y % 2 != 0:
                self._MT[i] ^= 0x9908b0df

if __name__ == '__main__':
    expectedNumbers = [int(x) for x in open('21.txt', 'r').read().split('\n')[:-1]]
    seed = 5489
    x = MT19937(seed)
    for i in range(1000):
        a = x.uint32()
        if a != expectedNumbers[i]:
            raise Exception(str(i) + ' ' + a + ' != ' + expectedNumbers[i])
