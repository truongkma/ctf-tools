#! /usr/bin/env python

from AES_128 import gen_rand_data, AES_128_CTR, AES_128_CTR

def get_unencrypted_data():
    from AES_128 import AES_128_ECB_decrypt
    from binascii import a2b_base64

    filename = '25.txt'
    key = 'YELLOW SUBMARINE'
    data = a2b_base64(''.join(l for l in open(filename)))
    return AES_128_ECB_decrypt(data, key, unpad = True)

key = gen_rand_data()
nonce = 0

def get_encrypted_data():
    data = get_unencrypted_data()
    return AES_128_CTR(data, key, nonce)

def edit(ciphertext, offset, newtext):
    data = AES_128_CTR(ciphertext, key, nonce)
    d = [c for c in data]
    newtext = [c for c in newtext]
    d[offset:offset+len(newtext)] = newtext
    data = ''.join(d)
    return AES_128_CTR(data, key, nonce)

if __name__ == '__main__':
    enc = get_encrypted_data()
    dec_edit = AES_128_CTR(edit(enc, 0, 'XYZAB'),key,nonce)
    if dec_edit[:5] == 'XYZAB':
        print '[+] Edit test passed. Found %s...' % repr(dec_edit[:10])
    else:
        print '[-] Edit test failed. Found %s...' % repr(dec_edit[:10])
