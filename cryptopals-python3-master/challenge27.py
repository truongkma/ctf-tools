from Crypto.Cipher import AES
import challenge10
import challenge15
import util

key = util.randbytes(16)

def encryptParams(userdata):
    userdata = userdata.replace(';', '%3B').replace('=', '%3D')
    x1 = b'comment1=cooking%20MCs;userdata='
    x2 = b';comment2=%20like%20a%20pound%20of%20bacon'
    params = x1 + userdata.encode('ascii') + x2
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), key)
    return cipher.encrypt(util.padPKCS7(params, 16))

def decryptParamsAndCheckAdmin(encryptedParams):
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), key)
    paddedParams = cipher.decrypt(encryptedParams)
    params = challenge15.unpadPKCS7(paddedParams)
    if any([x > 127 for x in params]):
        raise ValueError(params)
    return params.find(b';admin=true;') != -1

c = encryptParams('')
c = c[0:16] + (b'\x00' * 16) + c[0:16] + c[48:]
try:
    decryptParamsAndCheckAdmin(c)
    raise Exception('unexpected')
except ValueError as e:
    text = e.args[0]
    extracted_key = bytes([text[i] ^ text[32 + i] for i in range(16)])
    print(extracted_key)
    if extracted_key != key:
        raise Exception(extracted_key + ' != ' + key)
