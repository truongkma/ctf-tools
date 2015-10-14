#!/usr/bin/python

from challenge3 import brute_break as brute_break_str
from sys import maxint as MAX_NUM
from challenge5 import repeating_key_xor
from binascii import unhexlify
import itertools

def hamming_distance(a, b):
    xord = [ord(x)^ord(y) for x,y in zip(a,b)]
    return reduce(lambda mem, x: mem + bin(x).count('1'), xord, 0)

def guess_key_len(data):
    best_guess = (MAX_NUM, None)
    for guess in range(2,41):
        blocks = [data[i:i+guess] for i in range(0, len(data), guess)][0:4]
        pairs = list(itertools.combinations(blocks,2))
        score = sum(map(lambda x: hamming_distance(*x) / float(guess), pairs)) / float(len(pairs))
        if (score < best_guess[0]):
            best_guess = (score, guess)

    return best_guess[1]

def guess_key(data, key_len=None):
    key_len = guess_key_len(data) if key_len == None else key_len
    blocks = [data[i:i+key_len] for i in range(0, len(data)-key_len, key_len)]
    transposed = [''.join(i) for i in zip(*blocks)]
    return ''.join(map(lambda x: brute_break_str(x, ishex=False)[2], transposed))

def brute_break(data):
    key = guess_key(data)
    return unhexlify(repeating_key_xor(data, key))

if __name__ == '__main__':
    with open('./data/6.txt') as f:
        import base64
        print brute_break(base64.b64decode(f.read()))
