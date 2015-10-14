from Crypto.Random import random
import hashlib
import hmac as hmac_module

def getSalt():
    return random.getrandbits(64)

def hashToBytes(s):
    sha256 = hashlib.sha256()
    sha256.update(s.encode('ascii'))
    return sha256.digest()

def hashToInt(s):
    sha256 = hashlib.sha256()
    sha256.update(s.encode('ascii'))
    return int(sha256.hexdigest(), 16)

def hmac(salt, b):
    hmac_fn = hmac_module.new(str(salt).encode('ascii'), digestmod=hashlib.sha256)
    hmac_fn.update(b)
    return hmac_fn.digest()
