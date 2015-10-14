#! /usr/bin/env python

from binascii import a2b_hex, b2a_base64

print b2a_base64(a2b_hex(raw_input()))
