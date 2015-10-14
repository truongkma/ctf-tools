import challenge34_util
import socket
import socketserver
import sys

targethost = ''
targetport = 0
targetg = 0

class AttackerTCPHandler(socketserver.StreamRequestHandler):
    def handle(self):
        global targethost
        global targetport
        global targetg

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((targethost, targetport))
            serverutil = challenge34_util.Util(sock)
            clientutil = challenge34_util.Util(self)

            print('C->A: reading p...')
            p = clientutil.readnum()

            print('C->A: reading g...')
            g = clientutil.readnum()

            print('A->S: writing p...')
            serverutil.writenum(p)

            if targetg > 0:
                fakeg = 1
            elif targetg < 0:
                fakeg = p - 1
            else:
                fakeg = p

            print('A->S: writing fake g...')
            serverutil.writenum(fakeg)

            print('S->A: reading p...')
            serverutil.readnum()

            print('S->A: reading g...')
            serverutil.readnum()

            print('A->C: writing p...')
            clientutil.writenum(p)

            print('A->C: writing fake g...')
            clientutil.writenum(fakeg)

            print('C->A: reading A...')
            A = clientutil.readnum()

            print('A->S: writing A...')
            serverutil.writenum(A)

            print('S->A: reading B...')
            B = serverutil.readnum()

            print('A->C: writing B...')
            clientutil.writenum(B)

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

            if targetg > 0:
                s = 1
            elif targetg < 0:
                if A == p - 1 and B == p - 1:
                    s = p - 1
                else:
                    s = 1
            else:
                s = 0
            key = serverutil.derivekey(s)
            message = serverutil.decrypt(key, iv, encryptedMessage)

            print('A: message: ' + message)

        finally:
            sock.close()

if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2])
    targethost = sys.argv[3]
    targetport = int(sys.argv[4])
    targetg = int(sys.argv[5])

    print('listening on ' + host + ':' + str(port) + ', attacking ' + targethost + ':' + str(targetport))
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), AttackerTCPHandler)

    server.serve_forever()
