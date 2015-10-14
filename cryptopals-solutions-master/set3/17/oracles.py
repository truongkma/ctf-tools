#! /usr/bin/env python

import sys
from binascii import a2b_base64
from random import randint
from AES_128 import AES_128_CBC_decrypt, AES_128_CBC_encrypt, PaddingException

def gen_rand_data(length = 16):
  return ''.join(chr(randint(0,255)) for i in range(length))

key = gen_rand_data()

strings = ['MDAwMDAwTm93IHRoYXQgdGhlIHBhcnR5IGlzIGp1bXBpbmc=',
'MDAwMDAxV2l0aCB0aGUgYmFzcyBraWNrZWQgaW4gYW5kIHRoZSBWZWdhJ3MgYXJlIHB1bXBpbic=',
'MDAwMDAyUXVpY2sgdG8gdGhlIHBvaW50LCB0byB0aGUgcG9pbnQsIG5vIGZha2luZw==',
'MDAwMDAzQ29va2luZyBNQydzIGxpa2UgYSBwb3VuZCBvZiBiYWNvbg==',
'MDAwMDA0QnVybmluZyAnZW0sIGlmIHlvdSBhaW4ndCBxdWljayBhbmQgbmltYmxl',
'MDAwMDA1SSBnbyBjcmF6eSB3aGVuIEkgaGVhciBhIGN5bWJhbA==',
'MDAwMDA2QW5kIGEgaGlnaCBoYXQgd2l0aCBhIHNvdXBlZCB1cCB0ZW1wbw==',
'MDAwMDA3SSdtIG9uIGEgcm9sbCwgaXQncyB0aW1lIHRvIGdvIHNvbG8=',
'MDAwMDA4b2xsaW4nIGluIG15IGZpdmUgcG9pbnQgb2g=',
'MDAwMDA5aXRoIG15IHJhZy10b3AgZG93biBzbyBteSBoYWlyIGNhbiBibG93']

def encryption_oracle():
  data = a2b_base64(strings[randint(0,len(strings)-1)])
  iv  = gen_rand_data()
  return (iv, AES_128_CBC_encrypt(data, key, iv))

def padding_oracle(iv, data):
  try:
    AES_128_CBC_decrypt(data, key, iv)
    return True
  except PaddingException:
    return False

if __name__ == '__main__':
  iv, ciphertext = encryption_oracle()
  if padding_oracle(iv, ciphertext):
    print "Test 1 passed"
  iv, ciphertext = encryption_oracle()
  if padding_oracle(iv, ciphertext):
    print "Test 2 passed"
  ciphertext = [ord(c) for c in ciphertext]
  ciphertext[-1] = ciphertext[-1] ^ 1
  ciphertext = ''.join(chr(c) for c in ciphertext)
  if not padding_oracle(iv, ciphertext):
    print "Test 3 passed"

