import base64
from Crypto.Cipher import AES

x = base64.b64decode(open('7.txt', 'r').read())

key = b'YELLOW SUBMARINE'
cipher = AES.new(key, AES.MODE_ECB)
y = cipher.decrypt(x)
print(y)
