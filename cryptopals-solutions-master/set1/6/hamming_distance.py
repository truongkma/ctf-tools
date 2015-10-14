#! /usr/bin/env python

from binascii import b2a_hex

def hamming_distance(A, B):
  X = int(b2a_hex(A),16) ^ int(b2a_hex(B),16)
  return count_binary_ones(X)

def count_binary_ones(X):
  ret = 0
  while X != 0:
    ret = ret + 1
    X &= X-1  
  return ret

def normalized_hamming_distance (A, length): # Takes adjacent groups of 'length' length and finds avg hamming dist and normalizes it
  ham_sum = 0
  for i in range(len(A)/length - 1):
    ham_sum += hamming_distance(A[(i+0)*length:(i+1)*length], A[(i+1)*length:(i+2)*length])
  ham_avg = (1.0 * ham_sum) / (len(A)/length - 1)
  norm_ham = ham_avg / length
  return norm_ham

if __name__ == '__main__':
  if hamming_distance("this is a test","wokka wokka!!!") == 37:
    print "Hamming Distance tests pass"
  if normalized_hamming_distance("this is a testwokka wokka!!!",14) == 37.0/14:
    print "Normalized Hamming Distance tests pass"
