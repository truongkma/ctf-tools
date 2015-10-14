#! /usr/bin/env python

from mersenne import MT19937
from random import randint

def main():
    m = MT19937(randint(0,2**32-1))
    values = [m.random() for __ in range(624)]
    n = MT19937.generate_clone(values)

    for i in range(10):
        mr = m.random()
        nr = n.random()
        if mr != nr:
            print "[-] Test #%d failed. %d != %d" % (i, mr, nr)
        else:
            print "[+] Test #%d passed. %d matched." % (i, mr)

if __name__ == '__main__':
    main()
