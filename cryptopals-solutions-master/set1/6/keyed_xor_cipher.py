#! /usr/bin/env python

from binascii import b2a_hex, a2b_hex

def repeating_xor_cipher(text, key): # Note: text and key must be in binary, answer is in binary string
  length = len(text)
  
  while len(key) != length:
    for i in range(len(key)):
      if len(key) == length:
        break
      key = key + key[i]

  ret = ("%x" % (int(b2a_hex(text),16)^int(b2a_hex(key),16)))

  ret = "0"*(2*length-len(ret)) + ret

  return a2b_hex(ret)
