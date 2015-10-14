from Crypto.Random import random
import socket
import sys
import util
import challenge34_util

host = sys.argv[1]
port = int(sys.argv[2])
message = sys.argv[3]

p = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2
a = random.randint(0, p)
A = pow(g, a, p)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    sock.connect((host, port))
    util = challenge34_util.Util(sock)

    print('C: writing p...')
    util.writenum(p)

    print('C: writing g...')
    util.writenum(g)

    print('C: writing A...')
    util.writenum(A)

    print('C: reading B...')
    B = util.readnum()

    s = pow(B, a, p)
    key = util.derivekey(s)

    iv = util.randbytes(16)
    encryptedMessage = util.encrypt(key, iv, message)

    print('C: writing encrypted message...')
    util.writebytes(encryptedMessage)

    print('C: writing iv...')
    util.writebytes(iv)

    print('C: reading encrypted message...')
    encryptedMessage2 = util.readbytes()
    message2 = util.decrypt(key, iv, encryptedMessage2)
    if message2 != message:
        raise Exception(message2 + ' != ' + message)
finally:
    sock.close()
