from Crypto.Cipher import AES
import util

def encode_profile(profile):
    s = b''
    def sanitize(s):
        return s.replace(b'&', b'').replace(b'=', b'')
    for kv in profile:
        sanitizedKV = [sanitize(x.encode('ascii')) for x in kv]
        if s != b'':
            s += b'&'
        s += sanitizedKV[0] + b'=' + sanitizedKV[1]
    return s

def profile_for(email):
    profile = [
        ['email', email],
        ['uid', '10'],
        ['role', 'user']
        ]
    return encode_profile(profile)

key = util.randbytes(16)

def encrypt_profile_for(email):
    cipher = AES.new(key, AES.MODE_ECB)
    encoded_profile = util.padPKCS7(profile_for(email), 16)
    return cipher.encrypt(encoded_profile)

def unpadPKCS7(s, k):
    i = s[-1]
    return s[0:-i]

def decrypt_profile(s):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_profile = unpadPKCS7(cipher.decrypt(s), 16)
    pairs = decrypted_profile.split(b'&')
    profile = []
    for p in pairs:
        profile += [[x.decode('ascii') for x in p.split(b'=')]]
    return profile

email1 = 'foo@bar.coadmin' + ('\x0b' * 11)
x1 = encrypt_profile_for(email1)
email2 = 'foo@bar.commm'
x2 = encrypt_profile_for(email2)
x = x2[0:32] + x1[16:32]
y = decrypt_profile(x)
print(y)
