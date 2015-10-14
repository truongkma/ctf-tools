from Crypto.Random import random
import challenge39
import challenge43

# Doesn't check for 0 values for r and s.
def relaxedSign(message, pub, priv):
    H = challenge43.hash(message)
    (p, q, g, y) = pub
    k = random.randint(1, q-1)
    x = priv
    r = pow(g, k, p) % q
    kInv = challenge39.invmod(k, q)
    s = (kInv * (H + x * r)) % q
    return (r, s)

# Doesn't check for 0 values for r and s.
def relaxedVerifySignature(message, signature, pub):
    H = challenge43.hash(message)
    (r, s) = signature
    (p, q, g, y) = pub
    if r < 0 or r >= q or s < 0 or s >= q:
        return False
    w = challenge39.invmod(s, q)
    u1 = (H * w) % q
    u2 = (r * w) % q
    v = ((pow(g, u1, p) * pow(y, u2, p)) % p) % q
    return v == r

if __name__ == '__main__':
    (p, q, g) = (0x800000000000000089e1855218a0e7dac38136ffafa72eda7859f2171e25e65eac698c1702578b07dc2a1076da241c76c62d374d8389ea5aeffd3226a0530cc565f3bf6b50929139ebeac04f48c3c84afb796d61e5a4f9a8fda812ab59494232c7d2b4deb50aa18ee9e132bfa85ac4374d7f9091abc3d015efc871a584471bb1, 0xf4f47f05794b256174bba6e9b396a7707e563c5b, 0x5958c9d3898b224b12672c0b98e06c60df923cb8bc999d119458fef538b8fa4046c8db53039db620c094c9fa077ef389b5322a559946a71903f990f1f7e0e025e2d7f7cf494aff1a0470f5b64c36b625a097f1651fe775323556fe00b3608c887892878480e99041be601a62166ca6894bdd41a7054ec89f756ba9fc95302291)
    pub, priv = challenge43.genKeys(p, q, 0)
    message1 = b'Hello, world'
    signature1 = relaxedSign(message1, pub, priv)
    message2 = b'Goodbye, world'
    signature2 = relaxedSign(message2, pub, priv)
    print(message1, signature1, relaxedVerifySignature(message1, signature1, pub))
    print(message2, signature2, relaxedVerifySignature(message2, signature2, pub))
    print(relaxedVerifySignature(message1, signature2, pub))
    print(relaxedVerifySignature(message2, signature1, pub))

    pub, priv = challenge43.genKeys(p, q, p+1)
    (_, _, _, y) = pub
    z = 2
    invZ = challenge39.invmod(2, q)
    r = ((y**z) % p) % q
    s = (r * invZ) % q
    signature = (r, s)
    print(signature)
    print(message1, challenge43.verifySignature(message1, signature, pub))
    print(message2, challenge43.verifySignature(message2, signature, pub))
