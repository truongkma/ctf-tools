from Crypto.Random import random
import challenge34_util
import socket
import socketserver
import sys

targethost = ''
targetport = 0

class AttackerTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global targethost
        global targetport

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((targethost, targetport))
            serverutil = challenge34_util.Util(sock)
            clientutil = challenge34_util.Util(self)

            print('C->A: reading p...')
            p = clientutil.readnum()

            print('C->A: reading g...')
            g = clientutil.readnum()

            print('C->A: reading A...')
            A = clientutil.readnum()

            print('A->S: writing p...')
            serverutil.writenum(p)

            print('A->S: writing g...')
            serverutil.writenum(g)

            print('A->S: writing p...')
            serverutil.writenum(p)

            print('S->A: reading B...')
            B = serverutil.readnum()

            print('A->C: writing p...')
            clientutil.writenum(p)

            print('C->A: reading encrypted message...')
            encryptedMessage = clientutil.readbytes()

            print('A->S: writing encrypted message...')
            serverutil.writebytes(encryptedMessage)

            print('C->A: reading iv...')
            iv = clientutil.readbytes()

            print('A->S: writing iv...')
            serverutil.writebytes(iv)

            print('S->A: reading encrypted message...')
            encryptedMessage2 = serverutil.readbytes()

            print('A->C: writing encrypted message...')
            clientutil.writebytes(encryptedMessage2)

            print('S->A: reading iv...')
            iv2 = serverutil.readbytes()

            print('A->C: writing iv...')
            clientutil.writebytes(iv2)

            key = serverutil.derivekey(0)
            message = serverutil.decrypt(key, iv, encryptedMessage)

            print('A: message: ' + message)

        finally:
            sock.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    targethost = sys.argv[3]
    targetport = int(sys.argv[4])

    print('listening on ' + host + ':' + str(port) + ', attacking ' + targethost + ':' + str(targetport))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), AttackerTCPHandler)

    server.serve_forever()
