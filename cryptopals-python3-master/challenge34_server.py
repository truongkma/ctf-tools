from Crypto.Random import random
import challenge34_util
import socketserver
import sys

class DiffieHellmanTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        util = challenge34_util.Util(self)

        print('S: reading p...')
        p = util.readnum()

        print('S: reading g...')
        g = util.readnum()

        print('S: reading A...')
        A = util.readnum()

        b = random.randint(0, p)
        B = pow(g, b, p)

        print('S: writing B...')
        util.writenum(B)

        s = pow(A, b, p)
        key = util.derivekey(s)

        print('S: reading encrypted message...')
        encryptedMessage = util.readbytes()

        print('S: reading iv...')
        iv = util.readbytes()

        message = util.decrypt(key, iv, encryptedMessage)
        print('S: message:', message)

        encryptedMessage2 = util.encrypt(key, iv, message)
        if encryptedMessage2 != encryptedMessage:
            raise Exception(encryptedMessage2 + b' != ' + encryptedMessage)

        print('S: writing encrypted message...')
        util.writebytes(encryptedMessage2)

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])

    print('listening on ' + host + ':' + str(port))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), DiffieHellmanTCPHandler)

    server.serve_forever()
