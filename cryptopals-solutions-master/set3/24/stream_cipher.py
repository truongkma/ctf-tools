#! /usr/bin/env python

from mersenne import MT19937
from random import randint
import sys

key = randint(0,2**16-1)

def encrypt(data):
    m = MT19937(key)
    return ''.join(chr((m.random() % 256) ^ ord(d)) for d in data)

def decrypt(data):
    return encrypt(data)

def gen_rand_data(length):
    return ''.join(chr(randint(0,255)) for i in range(length))

def oracle(data):
    return encrypt(gen_rand_data(randint(0,5)) + data + gen_rand_data(randint(0,5)))

## Real crack begins here

def xor_data(A, B):
    return ''.join(chr(ord(A[i])^ord(B[i])) for i in range(len(A)))

def crack():
    length_of_input = 14

    encrypted = oracle('A'*length_of_input)
    length = len(encrypted)
    possible_keystream = xor_data(encrypted, 'A'*length)
    possible_keystream = [ord(p) for p in possible_keystream]

    possible_keys = []

    print "Progress: ",

    for k in range(2**16):
        m = MT19937(k)
        if sum([m.random() % 256 == p for p in possible_keystream]) >= length_of_input:
            possible_keys.append(k)
        if k % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()

    print
    print "Possible keys = %s" % (possible_keys)
    print "Real key = %s" % key
    print "Real key in possible keys = %s" % (key in possible_keys)

if __name__ == '__main__':
    crack()
