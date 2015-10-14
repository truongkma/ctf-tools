#! /usr/bin/env python

from random import randint
from oracles import encryption_oracle, decryption_oracle

def get_len_of_block_cipher(oracle): # Use probabilities and GCD to predict length of block
  from fractions import gcd
  length = None
  for i in range(256):
    l = len(oracle('A'*randint(0,256)))
    if length == None:
      length = l
    length = gcd(l, length)
  return length

def get_ignored_prefix_count(oracle, block_size):
  r1 = oracle('')
  r2 = oracle('A')

  for i in range(len(r1)):
    if r1[i] != r2[i]:
      common_prefix_len = i
      break

  return common_prefix_len/block_size

def find_block_allign_count(oracle, block_size, ignorable_blocks):
  for count in range(2*block_size):
    r = oracle('A'*count+'Y')[ignorable_blocks*block_size:]
    s = oracle('A'*count+'X')[ignorable_blocks*block_size:]
    if r[0:block_size] == s[0:block_size]:
      return count

def xor_data(A, B):
  if len(A) < len(B):
    return xor_data(B,A)
  return ''.join(chr(ord(A[i])^ord(B[i])) for i in range(len(A)))

def crack(e_oracle, d_oracle):
  block_size = get_len_of_block_cipher(e_oracle)
  print "[+] Block size = %d" % block_size

  # We want ';admin=true;' in the decrypted string
  # First, we make 'XadminXtrueX' come in one block
  # Then, we modify the previous block's correct positions to change to X's to the correct characters

  ignorable_blocks = get_ignored_prefix_count(e_oracle, block_size)
  print "[+] Ignorable blocks = %d" % ignorable_blocks

  block_allign_count = find_block_allign_count(e_oracle, block_size, ignorable_blocks)
  print "[+] Block allign count = %d" % block_allign_count

  joke_string = 'X'*block_size
  reqd_string = ';admin=true;'
  reqd_string += 'X'*(block_size-len(reqd_string))

  encrypted = e_oracle('A'*block_allign_count + 'B'*block_size + joke_string)

  modified_block = xor_data(xor_data(joke_string,reqd_string), encrypted[(ignorable_blocks+1)*block_size:(ignorable_blocks+2)*block_size]) # Modify the B's block

  attack = ''
  attack += encrypted[:(ignorable_blocks+1)*block_size] # Take everything until the A's
  attack += modified_block
  attack += encrypted[(ignorable_blocks+2)*block_size:] # Take rest of it directly

  if d_oracle(attack) == True:
    print "[+] Cracked"
  else:
    print "[-] Failed"

crack(encryption_oracle, decryption_oracle)
