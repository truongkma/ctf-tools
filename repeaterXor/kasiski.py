from collections import Counter
from encrypted import enc_ascii
from itertools import izip, cycle
from encrypted import enc_numbers

def shift(data, offset):
    return data[offset:] + data[:offset]

def count_same(a, b):
    count = 0
    for x, y in zip(a, b):
        if x == y:
            count += 1
    return count

print ('key lengths')
for key_len in range(1, 33): # try multiple key lengths
    freq = count_same(enc_numbers, shift(enc_numbers, key_len))
    print ('{0:< 3d} | {1:3d} |'.format(key_len, freq) + '=' * (freq / 4))
    # when we get the right key length, if there is repeating plaintext,
    # we have equal letters when we shift them over

key_len = 8
frequencies = []
for i in range(0, key_len):
    frequency = Counter()
    for ch in enc_ascii[i::key_len]:
        frequency[ch] += 1
    frequencies.append(frequency)

print ('guesses for most common letters')
key_numbers = []
for frequency in frequencies:
    k = ord(frequency.most_common(1)[0][0]) ^ ord(' ')
    print ('{k} -> \' \''.format(**locals()))
    key_numbers.append(k)
    
    others = ''
    for val, freq in frequency.most_common(10):
        others += chr(ord(val) ^ k) + ' '
    print ('Other common letters: {others}\n'.format(**locals()))

def decrypt(c_num, k_num):
    return ''.join(chr(c ^ k) for c, k in izip(c_num, cycle(k_num)))

print ('decrypting text')
print (decrypt(enc_numbers, key_numbers))
