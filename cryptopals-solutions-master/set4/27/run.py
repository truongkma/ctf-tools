#! /usr/bin/env python

from random import randint
from oracles import encryption_oracle, decryption_oracle, verify_key
from AES_128 import xor_data, PaddingException

def get_len_of_block_cipher(oracle): # Use probabilities and GCD to predict length of block
  from fractions import gcd
  length = None
  for i in range(256):
    l = len(oracle('A'*randint(0,256)))
    if length == None:
      length = l
    length = gcd(l, length)
  return length

def crack(e_oracle, d_oracle):
  block_size = get_len_of_block_cipher(e_oracle)
  print "[+] Block size = %d" % block_size

  input_plaintext = 'x'*(3*block_size)
  encrypted = e_oracle(input_plaintext)
  try:
    modified_encrypted = encrypted[0:block_size] + '\x00'*block_size + encrypted[0:block_size] + encrypted[block_size*2:]
    d_oracle(modified_encrypted)
    print "[-] An error should've occured. It didn't. Thereby, an error occurred."
  except PaddingException:
    print "[-] Something somewhere went terribly wrong"
  except ValueError as e: # This is where we attack
    recovered_plaintext = str(e)

  key = xor_data(recovered_plaintext[0:block_size], recovered_plaintext[block_size*2:block_size*3])

  if verify_key(key):
    print "[+] Cracked key = %s" % repr(key)
  else:
    print "[+] Cracking failed with = %s" % repr(key)

crack(encryption_oracle, decryption_oracle)
