#! /usr/bin/env python

import sys
from binascii import a2b_base64
from random import randint
from AES_128 import AES_128_CBC_decrypt, AES_128_CBC_encrypt, pkcs_7_unpad

def gen_rand_data(length = 16):
  return ''.join(chr(randint(0,255)) for i in range(length))

key = gen_rand_data()
iv  = gen_rand_data()

def encryption_oracle(data):
  data = data.replace(';','%3b')
  data = data.replace('=','%3d')
  data = "comment1=cooking%20MCs;userdata=" + data + ";comment2=%20like%20a%20pound%20of%20bacon"
  return AES_128_CBC_encrypt(data, key, iv)

def decryption_oracle(data):
  return (AES_128_CBC_decrypt(data, key, iv).count(';admin=true;') > 0)

if __name__ == '__main__':
  print "[>] encrypt() constancy tests:"
  tests   = ['', 'abc', ';admin=true;']
  for i in range(len(tests)):
    if encryption_oracle(tests[i]) == encryption_oracle(tests[i]):
      print "    [+] Test passed for %s" % repr(tests[i])
    else:
      print "    [-] Test failed for %s" % repr(tests[i])  

  print "[>] decrypt(encrypt()) == False tests:"
  tests   = ['', 'abc', ';admin=true;']
  for i in range(len(tests)):
    if decryption_oracle(encryption_oracle(tests[i])) == False:
      print "    [+] Test passed for %s" % repr(tests[i])
    else:
      print "    [-] Test failed for %s" % repr(tests[i])

  print "[>] decrypt() verification test:"
  if decryption_oracle(AES_128_CBC_encrypt(';admin=true;', key, iv)) == True:
    print "    [+] Test passed"
  else:
    print "    [-] Test failed"
