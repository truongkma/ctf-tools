#! /usr/bin/env python

from random import randint
import urllib
from AES_128 import AES_128_ECB_decrypt, AES_128_ECB_encrypt, pkcs_7_unpad

def gen_rand_data(length = 16):
  return ''.join(chr(randint(0,255)) for i in range(length))

key = gen_rand_data()

def encrypt(data):
  return AES_128_ECB_encrypt(data, key, True)

def decrypt(data):
  return AES_128_ECB_decrypt(data, key, True)

######################################################################################
# Parsing routines
######################################################################################

def parse_string(string):
  return dict(urllib.splitvalue(s) for s in string.split('&'))

def _profile_for(emailid):
  emailid = emailid.replace('&','')
  emailid = emailid.replace('=','')
  return urllib.urlencode([('email',emailid),('uid',10),('role','user')])

######################################################################################
# Oracle routines
######################################################################################

def profile_for(emailid):
  return encrypt(_profile_for(emailid))

def check_if_admin(data):
  val = (parse_string(decrypt(data))['role'] == 'admin')
  return val

######################################################################################
# Real crack begins after this
######################################################################################

def get_block(data, block_size, block_number):
  return data[block_number*block_size:(block_number+1)*block_size]

def crack(oracle):
  block_size = 16

  # 0123456789ABCDEF 0123456789ABCDEF 0123456789ABCDEF 0123456789ABCDEF
  # email=XXXme%40me .me&uid=10&role= admin&uid=10&rol ----------------      # This is the final aim (Note: '-' stands for padding byte)
  # email=XXXme%40me .me&uid=10&role= user------------                       # Email ID = XXXme@me.me   ; Useful block = 0 (place first), 1 (place second)
  # email=X%40X.XXXX admin&uid=10&rol e=user----------                       # Email ID = X@X.XXXXadmin ; Useful block = 1 (place third)
  # email=X%40XX.XX& uid=10&role=user ----------------                       # Email ID = X@XX.XX       ; Useful block = 2 (place fourth)


  res1 = oracle('XXXme@me.me')
  res2 = oracle('X@X.XXXXadmin')
  res3 = oracle('X@XX.XX')

  malicious = get_block(res1, block_size, 0) + get_block(res1, block_size, 1) + get_block(res2, block_size, 1) + get_block(res3, block_size, 2)

  if check_if_admin(malicious):
    print "[+] Successfully cracked"
  else:
    print "[-] Crack failed"

crack(profile_for)

# print check_if_admin(encrypt(urllib.urlencode([('email','abc@def.com'),('uid',10),('role','user'),('role','admin')]))) # Sanity check... Should give True
