from Crypto.Random import random

def randbytes(k):
    return random.getrandbits(8*k).to_bytes(k, byteorder='big')

def padPKCS7(x, k):
    ch = k - (len(x) % k)
    return x + bytes([ch] * ch)
