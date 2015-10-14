#! /usr/bin/env python

from stream_cipher import crack

def main():
  crack()
  print "In regards to the password token thing, it would be another matter of searching a small keyspace in a similar way. Implementation of this has been skipped since it would involve trivial modifications of the stream cipher crack above"

if __name__ == '__main__':
    main()
