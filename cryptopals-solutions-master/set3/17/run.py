#! /usr/bin/env python

from random import randint
from oracles import encryption_oracle, padding_oracle
from AES_128 import pkcs_7_unpad

# Note: These oracles return and take 2 things (iv, ciphertext) instead of 1 like in previous oracles

def xor_data(A, B):
  if len(A) < len(B):
    return xor_data(B,A)
  return ''.join(chr(ord(A[i])^ord(B[i])) for i in range(len(A)))

def set_last_bytes(last_bytes, guess_last_bytes, prev_block, curr_block):
  block = prev_block[:-len(last_bytes)]
  block += xor_data(
            xor_data(last_bytes, guess_last_bytes),
            prev_block[-len(last_bytes):]
           )
  return block

def crack_block(poracle, prev_block, curr_block):
  possible_last_bytes = []
  for i in range(256):
    if poracle(set_last_bytes('\x01',chr(i),prev_block, curr_block), curr_block):
      possible_last_bytes.append(chr(i))
  if len(possible_last_bytes) != 1:
    for l in possible_last_bytes:
      for i in range(256):
        if poracle(set_last_bytes('\x02\x02',chr(i)+l,prev_block, curr_block), curr_block):
          possible_last_bytes = [l]

  known_bytes = possible_last_bytes[0]

  for i in range(len(curr_block)-1):
    pad_val = len(known_bytes)+1
    pad = chr(pad_val)*pad_val
    for i in range(256):
      if poracle(set_last_bytes(pad,chr(i)+known_bytes,prev_block, curr_block), curr_block):
        known_bytes = chr(i)+known_bytes
        break

  return known_bytes # Temp

def crack_message(poracle, iv, ciphertext):
  blocks = [iv]
  block_size = len(iv)
  for i in range(len(ciphertext) / block_size):
    blocks.append(ciphertext[i*block_size:(i+1)*block_size])

  cracked_blocks = []

  for i in range(1,len(blocks)):
    cracked_blocks.append(crack_block(poracle,blocks[i-1],blocks[i]))

  return pkcs_7_unpad(''.join(cracked_blocks))

def crack(e_oracle, p_oracle):
  block_size = len(e_oracle()[0])
  print "[+] Block size = %d" % block_size

  cracked_messages = []

  while len(cracked_messages) < 10: # We *somehow* know this in advance
    iv, ciphertext = e_oracle()
    message = crack_message(p_oracle, iv, ciphertext)
    if not message in cracked_messages:
      cracked_messages.append(message)
      print "[+] Cracked: %s" % repr(message)

crack(encryption_oracle, padding_oracle)
