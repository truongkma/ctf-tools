#! /usr/bin/env python

from oracle import get_encrypted_data, edit
import sys

def recover_char_at(offset, enc):
    modification_char = 'x'

    original_encoding = enc[offset]
    new_encoding = edit(enc, offset, modification_char)[offset]

    recovered_char = chr(ord(modification_char) ^ ord(original_encoding)
                     ^ ord(new_encoding))

    return recovered_char

def alternate_main(): # Slower recovery
    enc = get_encrypted_data()
    length = len(enc)

    print '[+] Length of data = %d' % length
    print '[+] Recovering data'

    data = []
    for i in range(length):
        recovered_char = recover_char_at(i, enc)
        data.append(recovered_char)
        sys.stdout.write(recovered_char)

    data = ''.join(data)

    print '[+] Finished recovering data'

def main(): # Fast recovery
    from AES_128 import xor_data

    enc = get_encrypted_data()
    length = len(enc)

    print '[+] Length of data = %d' % length
    print '[+] Recovering data'

    modification_string = 'x'*length
    new_enc = edit(enc, 0, modification_string)

    data = xor_data(xor_data(enc, new_enc), modification_string)

    print data

    print '[+] Finished recovering data'

if __name__ == '__main__':
    main()
