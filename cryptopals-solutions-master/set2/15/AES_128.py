#! /usr/bin/env python

from Crypto.Cipher import AES
from binascii import a2b_base64

def pkcs_7_pad(data, final_len = None):
  if final_len == None:
    final_len = (len(data)/16 + 1)*16
  padding_len = final_len - len(data)
  return data + chr(padding_len)*padding_len

class PaddingException(Exception):
  """ Padding for input data incorrect """

def pkcs_7_unpad(data):
  padding_len = ord(data[len(data)-1])
  for i in range(len(data)-padding_len,len(data)):
    if ord(data[i]) != padding_len:
      raise PaddingException
  return data[:-padding_len]

def AES_128_ECB_encrypt(data, key, pad = False):
  cipher = AES.new(key, AES.MODE_ECB)
  if pad:
    data = pkcs_7_pad(data)
  return cipher.encrypt(data)

def AES_128_ECB_decrypt(data, key, unpad = False):
  cipher = AES.new(key, AES.MODE_ECB)
  decr = cipher.decrypt(data)
  if unpad:
    decr = pkcs_7_unpad(decr)
  return decr

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

if __name__ == '__main__':
  text = 'abcdefghijklmnopqrstuvwxyz!'
  key = 'abcdef1234567890'
  iv = '128348347dhrughdf'
  if AES_128_CBC_decrypt(AES_128_CBC_encrypt(text, key, iv), key, iv) == text:
    print "[+] CBC decrypt(encrypt(text))==text test passed"
  else:
    print "[-] CBC test failed"

