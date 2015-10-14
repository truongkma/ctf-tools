#! /usr/bin/env python

from SHA1 import SHA1_hexdigest

def main():
  print 'Input message:',
  message = raw_input()
  key = 'tempkey'
  print "SHA1(key || %s) = %s" % (repr(message), SHA1_hexdigest(key + message))

if __name__ == '__main__':
  main()
