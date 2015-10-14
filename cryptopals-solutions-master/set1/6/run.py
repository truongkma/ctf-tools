#! /usr/bin/env python

from binascii import a2b_base64
from hamming_distance import normalized_hamming_distance
from single_key_xor import single_xor_decode
from keyed_xor_cipher import repeating_xor_cipher

data = ""
filename = '6.txt'
for line in open(filename):
  data += line.strip()
data = a2b_base64(data)
best_hamming_dist = float('inf')
for KEYSIZE in range(2,80):
  ham = normalized_hamming_distance(data,KEYSIZE)
  if ham < best_hamming_dist:
    best_hamming_dist = ham
    best_keysize = KEYSIZE

KEYSIZE = best_keysize

print "[#] Inferred KEYSIZE = " + str(KEYSIZE)

split_data = [data[i::KEYSIZE] for i in range(KEYSIZE)]

decoded_data = [single_xor_decode(d, min(len(d),200)) for d in split_data] # Why 200, coz the strings start with 200 useless characters

key = ''.join(d[0] for d in decoded_data)
decoded_data = repeating_xor_cipher(data, key)

print "[#] Key = \"" + key + "\""
print "----------- DECODED DATA BEGIN ----------"
print decoded_data.strip()
print "------------ DECODED DATA END -----------"
