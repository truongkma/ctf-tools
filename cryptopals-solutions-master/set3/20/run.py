#! /usr/bin/env python

from AES_128 import AES_128_CTR, gen_rand_data
from binascii import a2b_base64
from random import randint
from xor_crack import get_choices_for_single_xor, xor_data

def initialize():
  global ciphertexts
  key = gen_rand_data()
  nonce = randint(0,2**64-1)
  ciphertexts = [AES_128_CTR(a2b_base64(p.strip()), key, nonce) for p in open('20.txt')]

def get_choice(pos):
  ctext = [c[pos] for c in ciphertexts if pos < len(c)]
  return get_choices_for_single_xor(ctext)

def crack():
  min_len_ciphertext = min(len(c) for c in ciphertexts)
  print "[+] Minimum length of ciphertext = %d" % min_len_ciphertext
  max_len_ciphertext = max(len(c) for c in ciphertexts)
  print "[+] Maximum length of ciphertext = %d" % max_len_ciphertext
  print "[+] Analyzing possible keys"
  choices = [get_choice(pos) for pos in range(max_len_ciphertext)]

  chosen = [0 for __ in range(max_len_ciphertext)]

  length_sorted_ciphertexts = sorted(ciphertexts, key=len)

  while True:
    key = [chr(c[chosen[i]]) for i, c in enumerate(choices)]
    for c in length_sorted_ciphertexts:
      print xor_data(c,key)
    inp = raw_input().rstrip()
    if len(inp) == 0:
      break
    for i, c in enumerate(inp):
      if c == 'v':
        chosen[i] -= 1
        chosen[i] %= len(choices[i])
      if c == '^':
        chosen[i] += 1
        chosen[i] %= len(choices[i])

  return [xor_data(c,key) for c in ciphertexts]

if __name__ == '__main__':
  initialize()
  print "[+] Initialization Done. Loaded %d ciphertexts." % len(ciphertexts)  
  plaintexts = crack()
  print "----- CRACKED TEXT BEGIN -----"
  for p in plaintexts:
    print p
  print "-----  CRACKED TEXT END  -----"
