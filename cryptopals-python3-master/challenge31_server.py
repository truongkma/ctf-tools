from Crypto.Util.strxor import strxor_c
from Crypto.Util.strxor import strxor
import binascii
import challenge28
import http.server
import socketserver
import time
import urllib.parse
import util

PORT = 9000
DELAY = 0.05

blocksize = 64
key = util.randbytes(100)

def sha1(x):
    return challenge28.SHA1(x).digest()

def hmacSHA1(key, message):
    if len(key) > blocksize:
        key = sha1(key)
    if len(key) < blocksize:
        key += b'\x00' * (blocksize - len(key))

    opad = strxor_c(key, 0x5c)
    ipad = strxor_c(key, 0x36)

    return sha1(opad + sha1(ipad + message))

def insecure_compare(x, y):
    if len(x) != len(y):
        return False
    for i in range(len(x)):
        if x[i] != y[i]:
            return False
        time.sleep(DELAY)
    return True

last_file = b''

class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global last_file
        result = urllib.parse.urlparse(self.path)
        if result.path == '/test':
            q = urllib.parse.parse_qs(result.query)
            file = q['file'][0].encode('ascii')
            digest = hmacSHA1(key, file)
            signature = binascii.unhexlify(q['signature'][0])
            if file != last_file:
                last_file = file
                print('New file:', file, binascii.hexlify(digest))
            print(binascii.hexlify(digest), binascii.hexlify(signature))
            if insecure_compare(digest, signature):
                self.send_error(200)
            else:
                self.send_error(500)
        else:
            self.send_error(500)

def serve_forever(delay):
    global DELAY
    DELAY = delay
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("", PORT), RequestHandler)
    print("serving at port {0} with delay {1}".format(PORT, DELAY))
    httpd.serve_forever()

if __name__ == '__main__':
    serve_forever(DELAY)
