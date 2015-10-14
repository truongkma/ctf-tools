#! /usr/bin/env python

import sys
from binascii import a2b_base64
from random import randint
from AES_128 import AES_128_CBC_decrypt, AES_128_CBC_encrypt, pkcs_7_unpad, gen_rand_data

key = gen_rand_data()
iv  = key

def check_high_ascii(data):
  for d in data:
    if ord(d) > 127:
      raise ValueError(data)

def encryption_oracle(data):
  data = data.replace(';','%3b')
  data = data.replace('=','%3d')
  check_high_ascii(data)
  return AES_128_CBC_encrypt(data, key, iv)

def decryption_oracle(data):
  decrypted_plaintext = AES_128_CBC_decrypt(data, key, iv)
  check_high_ascii(decrypted_plaintext)
  return True # Decryption succeeded

def verify_key(test_key):
  return test_key == key

if __name__ == '__main__':
  print "[>] encrypt() constancy tests:"
  tests   = ['', 'abc', ';admin=true;']
  for i in range(len(tests)):
    if encryption_oracle(tests[i]) == encryption_oracle(tests[i]):
      print "    [+] Test passed for %s" % repr(tests[i])
    else:
      print "    [-] Test failed for %s" % repr(tests[i])

  print "[>] decrypt(encrypt()) == True tests:"
  tests   = ['', 'abc', ';admin=true;']
  for i in range(len(tests)):
    if decryption_oracle(encryption_oracle(tests[i])) == True:
      print "    [+] Test passed for %s" % repr(tests[i])
    else:
      print "    [-] Test failed for %s" % repr(tests[i])

  print "[>] High ASCII verification test:"
  tests   = ['', 'abc', ';admin=true;']
  for i in range(len(tests)):
    try:
      encryption_oracle(tests[i])
      print "    [+] Test passed for %s" % repr(tests[i])
    except ValueError as e:
      print "    [-] Test failed for %s. Found high ASCII in %s" % (repr(tests[i]), repr(e.args[0]))
  tests   = ['\xF0', 'a\xFFbc', ';admin\xA2=true;']
  for i in range(len(tests)):
    try:
      encryption_oracle(tests[i])
      print "    [-] Test failed for %s. No high ascii found." % repr(tests[i])
    except ValueError as e:
      print "    [+] Test passed for %s." % repr(e.args[0])
