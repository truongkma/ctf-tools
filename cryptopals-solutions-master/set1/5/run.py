#! /usr/bin/env python

from binascii import b2a_hex, a2b_hex

def repeating_xor_cipher(text, key): # Note: text and key must be in hex, answer will be in hex
  text = a2b_hex(text)
  key = a2b_hex(key)
  length = len(text)
  
  while len(key) != length:
    for i in range(len(key)):
      if len(key) == length:
        break
      key = key + key[i]

  ret = ("%x" % (int(b2a_hex(text),16)^int(b2a_hex(key),16)))

  ret = "0"*(2*length-len(ret)) + ret

  return ret

print "Input key: "
key = b2a_hex(raw_input())
print "Input filename: "
input_string = ""
for line in open(raw_input()):
  input_string = input_string + line

print "Encrypted: "
print repeating_xor_cipher(b2a_hex(input_string.rstrip()), key)

