import gmpy
import pyasn1_modules.rfc3447
import pyasn1.codec.ber.encoder
import base64


def asn1encodeprivkey(N, e, d, p, q):
    key = pyasn1_modules.rfc3447.RSAPrivateKey()
    dp = d % (p - 1)
    dq = d % (q - 1)
    qInv = gmpy.invert(q, p)
    assert (qInv * q) % p == 1
    key.setComponentByName('version', 0)
    key.setComponentByName('modulus', N)
    key.setComponentByName('publicExponent', e)
    key.setComponentByName('privateExponent', d)
    key.setComponentByName('prime1', p)
    key.setComponentByName('prime2', q)
    key.setComponentByName('exponent1', dp)
    key.setComponentByName('exponent2', dq)
    key.setComponentByName('coefficient', qInv)
    ber_key = pyasn1.codec.ber.encoder.encode(key)
    pem_key = base64.b64encode(ber_key).decode("ascii")
    out = ['-----BEGIN RSA PRIVATE KEY-----']
    out += [pem_key[i:i + 64] for i in range(0, len(pem_key), 64)]
    out.append('-----END RSA PRIVATE KEY-----\n')
    out = "\n".join(out)
    f = open('newkey.pem', 'wb')
    f.write(out.encode("ascii"))
    f.close
    return out.encode("ascii")
