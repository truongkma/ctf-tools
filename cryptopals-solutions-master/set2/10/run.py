#! /usr/bin/env python

from Crypto.Cipher import AES
from binascii import a2b_base64

def AES_128_ECB_encrypt(data, key):
  cipher = AES.new(key, AES.MODE_ECB)
  return cipher.encrypt(data)

def AES_128_ECB_decrypt(data, key):
  cipher = AES.new(key, AES.MODE_ECB)
  return cipher.decrypt(data)

def pkcs_7_pad(data, final_len = None):
  if final_len == None:
    final_len = (len(data)/16 + 1)*16
  padding_len = final_len - len(data)
  return data + chr(padding_len)*padding_len

def pkcs_7_unpad(data):
  padding_len = ord(data[len(data)-1])
  for i in range(len(data)-padding_len,len(data)):
    if ord(data[i]) != padding_len:
      return data
  return data[:-padding_len]

def xor_data(A, B):
  return ''.join(chr(ord(A[i])^ord(B[i])) for i in range(len(A)))

def AES_128_CBC_encrypt(data, key, iv):
  data = pkcs_7_pad(data)
  block_count = len(data)/16
  encrypted_data = ''
  prev_block = iv
  for b in range(block_count):
    cur_block = data[b*16:(b+1)*16]
    encrypted_block = AES_128_ECB_encrypt(xor_data(cur_block, prev_block), key)
    encrypted_data += encrypted_block
    prev_block = encrypted_block
  return encrypted_data

def AES_128_CBC_decrypt(data, key, iv):
  block_count = len(data)/16
  decrypted_data = ''
  prev_block = iv
  for b in range(block_count):
    cur_block = data[b*16:(b+1)*16]
    decrypted_block = AES_128_ECB_decrypt(cur_block, key)
    decrypted_data += xor_data(decrypted_block, prev_block)
    prev_block = cur_block
  return pkcs_7_unpad(decrypted_data)

filename = '10.txt'
key = 'YELLOW SUBMARINE'
data = a2b_base64(''.join(line.strip() for line in open(filename)))
iv = '\x00'*16
print AES_128_CBC_decrypt(data, key, iv).strip()

# print AES_128_CBC_decrypt(AES_128_CBC_encrypt('abcdefghijklmnopqrstuvwxyz!', 'abcdef1234567890', '128348347dhrughdf'), 'abcdef1234567890', '128348347dhrughdf') # Testing sanity
