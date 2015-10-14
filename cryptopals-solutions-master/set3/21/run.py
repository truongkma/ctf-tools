#! /usr/bin/env python

from mersenne import MT19937

for seed in range(5):
    m = MT19937(seed)
    print "%d : %s" % (seed, [m.random() for __ in range(5)])
