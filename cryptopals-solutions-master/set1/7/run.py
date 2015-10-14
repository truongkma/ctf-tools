#! /usr/bin/env python

from Crypto.Cipher import AES
from binascii import a2b_base64

def AES_128_ECB_decrypt(data, key):
  cipher = AES.new(key, AES.MODE_ECB)
  return cipher.decrypt(data)

filename = '7.txt'
key = 'YELLOW SUBMARINE'
data = a2b_base64(''.join(line.strip() for line in open(filename)))
print AES_128_ECB_decrypt(data, key)
