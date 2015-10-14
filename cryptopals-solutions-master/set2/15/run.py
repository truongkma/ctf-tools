#! /usr/bin/env python

from AES_128 import pkcs_7_unpad, PaddingException

cases = [
  "ICE ICE BABY\x04\x04\x04\x04",
  "ICE ICE BABY\x05\x05\x05\x05",
  "ICE ICE BABY\x01\x02\x03\x04"
]

for i in range(len(cases)):
  try:
    print "Case %d passed. String = %s" % (i, repr(pkcs_7_unpad(cases[i])))
  except PaddingException:
    print "Case %d went wrong. Caught PaddingException." % i
