#! /usr/bin/env python

from binascii import a2b_base64
from random import randint
from AES_128 import AES_128_CBC_encrypt, AES_128_ECB_encrypt, pkcs_7_unpad

def gen_rand_data(length = 16):
  return ''.join(chr(randint(0,255)) for i in range(length))

def encryption_oracle(data):
  if not hasattr(encryption_oracle, "key"):
    encryption_oracle.key = gen_rand_data()
  data = data + a2b_base64(
    'Um9sbGluJyBpbiBteSA1LjAKV2l0aCBteSByYWctdG9wIGRvd24gc28gbXkg'+
    'aGFpciBjYW4gYmxvdwpUaGUgZ2lybGllcyBvbiBzdGFuZGJ5IHdhdmluZyBq'+
    'dXN0IHRvIHNheSBoaQpEaWQgeW91IHN0b3A/IE5vLCBJIGp1c3QgZHJvdmUg'+
    'YnkK')
  return AES_128_ECB_encrypt(data, encryption_oracle.key, True)

######################################################################################
# Real crack begins after this
######################################################################################

def get_len_of_block_cipher(oracle):
  inp = ''
  prev_len = None
  while True:
    enc = oracle(inp)
    inp += 'A'
    l = len(enc)
    if prev_len != None and l > prev_len:
      return l - prev_len
    else:
      prev_len = l

def is_ECB_encoded(data, block_size):
  block_count = len(data)/block_size
  for i in range(block_count):
    for j in range(i+1,block_count):
      if data[i*block_size:(i+1)*block_size] == data[j*block_size:(j+1)*block_size]:
        return True
  return False

def verify_ECB_mode(oracle, block_size):
  inp = 'A'*(3*block_size)
  return is_ECB_encoded(oracle(inp),block_size)

def pull_next_letter(oracle, block_size, known_plaintext_prefix):
  required_prefix_len = (block_size - (1 + len(known_plaintext_prefix))) % block_size
  fixed_prefix = 'A'*required_prefix_len

  tested_block_len = len(fixed_prefix) + len(known_plaintext_prefix) + 1

  real_text = oracle(fixed_prefix)[:tested_block_len]

  for i in range(256):
    attack_text = fixed_prefix + known_plaintext_prefix + chr(i)
    if real_text == oracle(attack_text)[:tested_block_len]:
      return chr(i)

def crack(oracle):
  block_size = get_len_of_block_cipher(oracle)
  print "[+] Identified block size = " + str(block_size)
  if not verify_ECB_mode(oracle, block_size):
    print "[-] Not ECB encryption oracle"
    return
  else:
    print "[+] Verified ECB encryption"

  complete_message_len = len(oracle(''))

  message = ''
  for i in range(complete_message_len):
    try:
      message += pull_next_letter(oracle, block_size, message)
    except:
      break

  return pkcs_7_unpad(message)

print "----- DECRYPTED TEXT START -----\n" + crack(encryption_oracle) + "------ DECRYPTED TEXT END ------"
