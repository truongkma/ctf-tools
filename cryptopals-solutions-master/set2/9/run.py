#! /usr/bin/env python

def pkcs_7_pad(data, final_len):
  padding_len = final_len - len(data)
  return data + chr(padding_len)*padding_len

print repr(pkcs_7_pad("YELLOW SUBMARINE",20)) # The repr makes the output look nicer :)
