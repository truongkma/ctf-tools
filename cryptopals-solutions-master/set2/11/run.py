#! /usr/bin/env python

from random import randint # randint() takes 2 args which specify inclusive end points
from AES_128 import AES_128_CBC_encrypt, AES_128_ECB_encrypt

def gen_rand_data(length = 16):
  return ''.join(chr(randint(0,255)) for i in range(length))

tester_CBC = 'UNINITIALIZED' # Used for verifying whether code really works

def encryption_oracle(data):
  global tester_CBC
  should_encrypt_using_CBC = (randint(0,1)==0)
  key = gen_rand_data()

  data = gen_rand_data(randint(5,10)) + data + gen_rand_data(randint(5,10))

  if should_encrypt_using_CBC:
    iv = gen_rand_data()
    tester_CBC = "CBC"
    return AES_128_CBC_encrypt(data, key, iv)
  else:
    tester_CBC = "ECB"
    return AES_128_ECB_encrypt(data, key, True)

def is_ECB_encoded(data, block_size):
  block_count = len(data)/block_size
  for i in range(block_count):
    for j in range(i+1,block_count):
      if data[i*block_size:(i+1)*block_size] == data[j*block_size:(j+1)*block_size]:
        return True
  return False

def identify_ECB_or_CBC(oracle):
  block_length = 16
  # To make at least 2 encrypted blocks match, we need to put 3 blocks of matching plaintext
  plain_text = 'A'*(3*block_length)
  cipher_text = oracle(plain_text)
  if is_ECB_encoded(cipher_text, 16):
    return "ECB"
  else:
    return "CBC"

for i in range(10):
  is_ECB = identify_ECB_or_CBC(encryption_oracle)
  if is_ECB != tester_CBC:
    print "Failed on testcase " + str(i) + ". Guessed as " + guessedmode + " instead of " + tester_CBC + "."
  else:
    print "Identified " + tester_CBC + " correctly"
