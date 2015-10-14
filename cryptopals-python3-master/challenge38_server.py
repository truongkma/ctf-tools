from Crypto.Random import random
import challenge34_util
import challenge36_util
import socketserver
import sys

email = ''
password = ''
salt = 0
v = 0

N = 0xffffffffffffffffc90fdaa22168c234c4c6628b80dc1cd129024e088a67cc74020bbea63b139b22514a08798e3404ddef9519b3cd3a431b302b0a6df25f14374fe1356d6d51c245e485b576625e7ec6f44c42e9a637ed6b0bff5cb6f406b7edee386bfb5a899fa5ae9f24117c4b1fe649286651ece45b3dc2007cb8a163bf0598da48361c55d39a69163fa8fd24cf5f83655d23dca3ad961c62f356208552bb9ed529077096966d670c354e4abc9804f1746c08ca237327ffffffffffffffff
g = 2
k = 3

class SRPTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global email
        global password

        util = challenge34_util.Util(self)

        print('S: reading email...')
        readEmail = util.readline()

        print('S: reading A...')
        A = util.readnum()

        print('S: writing salt...')
        util.writenum(salt)

        b = random.randint(0, N)
        B = pow(g, b, N)

        print('S: writing B...')
        util.writenum(B)

        u = random.getrandbits(128)

        print('S: writing u...')
        util.writenum(u)

        S = pow(pow(v, u, N) * A, b, N)
        K = challenge36_util.hashToBytes(str(S))
        server_hmac = challenge36_util.hmac(salt, K)

        print('S: reading hmac...')
        client_hmac = util.readbytes()

        if client_hmac == server_hmac:
            print('S: writing success...')
            util.writeline(b'OK')
        else:
            util.writeline(b'NOT OK')

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    email = sys.argv[3]
    password = sys.argv[4]

    salt = challenge36_util.getSalt()
    x = challenge36_util.hashToInt(str(salt) + password)
    v = pow(g, x, N)

    print('listening on ' + host + ':' + str(port))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), SRPTCPHandler)

    server.serve_forever()
