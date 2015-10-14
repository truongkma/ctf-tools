from Crypto.Cipher import AES
import challenge10
import challenge15
import util

key = util.randbytes(16)
iv = util.randbytes(16)

def encryptParams(userdata):
    userdata = userdata.replace(';', '%3B').replace('=', '%3D')
    x1 = b'comment1=cooking%20MCs;userdata='
    x2 = b';comment2=%20like%20a%20pound%20of%20bacon'
    params = x1 + userdata.encode('ascii') + x2
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), iv)
    return cipher.encrypt(util.padPKCS7(params, 16))

def decryptParamsAndCheckAdmin(encryptedParams):
    cipher = challenge10.CBC(AES.new(key, AES.MODE_ECB), iv)
    paddedParams = cipher.decrypt(encryptedParams)
    params = challenge15.unpadPKCS7(paddedParams)
    return params.find(b';admin=true;') != -1

x = list(encryptParams('XXXXXXXXXXXXXXXX:admin<true:XXXX'))
x[32] ^= 1
x[38] ^= 1
x[43] ^= 1
print(decryptParamsAndCheckAdmin(bytes(x)))
