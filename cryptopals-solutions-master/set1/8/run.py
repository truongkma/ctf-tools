#! /usr/bin/env python

from binascii import a2b_hex

def is_ECB_encoded(data, block_size):
  block_count = len(data)/block_size
  for i in range(block_count):
    for j in range(i+1,block_count):
      if data[i*block_size:(i+1)*block_size] == data[j*block_size:(j+1)*block_size]:
        return True
  return False

filename = '8.txt'
for line in open(filename):
  line = line.strip()
  if is_ECB_encoded(a2b_hex(line), 16):
    print line
