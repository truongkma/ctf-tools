#! /usr/bin/env python

from AES_128 import AES_128_CTR
from binascii import a2b_base64

key = 'YELLOW SUBMARINE'
nonce = 0
cipher = a2b_base64('L77na/nrFsKvynd6HzOoG7GHTLXsTVu9qvY/2syLXzhPweyyMTJULu/6/kXX0KSvoOLSFQ==')

print "[+] Decrypted: %s" % repr(AES_128_CTR(cipher, key, nonce))
