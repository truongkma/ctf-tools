#! /usr/bin/env python

from random import randint
from oracles import encryption_oracle, decryption_oracle
from AES_128 import xor_data
from sys import exit

def get_constant_regions(e_oracle, length_of_insertion):
  enc_A = e_oracle('A'*length_of_insertion)
  enc_B = e_oracle('B'*length_of_insertion)

  if len(enc_A) != len(enc_B):
    print "[!] Oracle does not seem consistent"
    print "    enc('A') = %s" % repr(enc_A)
    print "    enc('B') = %s" % repr(enc_B)
    exit()

  left_half = []

  for i in range(len(enc_A)):
    if enc_A[i] == enc_B[i]:
      left_half.append(enc_A[i])
    else:
      break

  left_half = ''.join(left_half)
  right_half = enc_A[len(left_half)+length_of_insertion:]

  return (left_half, right_half)

def get_central_oracle(e_oracle):
  enc_A = e_oracle('A')
  enc_B = e_oracle('B')

  for i in range(len(enc_A)):
    if enc_A[i] != enc_B[i]:
      offset = i

  def central_oracle(data):
    return e_oracle(data)[offset:offset+len(data)]

  return central_oracle

def crack(e_oracle, d_oracle):
  injection_string = ';admin=true;'

  constant_regions = get_constant_regions(e_oracle, len(injection_string))

  central_oracle = get_central_oracle(e_oracle)

  joke_string = 'X'*len(injection_string)
  modified_ciphertext = xor_data(xor_data(joke_string, injection_string), central_oracle(joke_string))

  attack = ''
  attack += constant_regions[0]
  attack += modified_ciphertext
  attack += constant_regions[1]

  if d_oracle(attack) == True:
    print "[+] Cracked using %s" % repr(attack)
  else:
    print "[-] Failed using %s" % repr(attack)

crack(encryption_oracle, decryption_oracle)
