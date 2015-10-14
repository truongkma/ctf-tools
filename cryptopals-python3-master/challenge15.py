def unpadPKCS7(s):
    i = s[-1]
    if i == 0 or s[-i:] != bytes([i] * i):
        raise ValueError('bad padding')
    return s[0:-i]

if __name__ == '__main__':
    print(unpadPKCS7(b'ICE ICE BABY\x04\x04\x04\x04'))
    try:
        unpadPKCS7(b'ICE ICE BABY\x05\x05\x05\x05')
        raise Exception('passes unexpectedly')
    except ValueError:
        pass
    try:
        unpadPKCS7(b'ICE ICE BABY\x01\x02\x03\x04')
        raise Exception('passes unexpectedly')
    except ValueError:
        pass
