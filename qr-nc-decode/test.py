from PIL import Image
import qrtools
import telnetlib
import re
def getQR(qr):
    im = Image.new("RGB", (94, 94), 'white')
    pixels = im.load()
    y = 0
    x = 0
    i = 0
    while i < len(qr):
        if qr[i] == '\xe2':
            pixels[x,y] = (0, 0, 0)
            pixels[x,y+1] = (0, 0, 0)
            x += 1
        if qr[i] == '\x20':
            pixels[x,y] = (255, 255, 255)
            pixels[x,y+1] = (255, 255, 255)
            x += 1
        if qr[i] == '\n':
            x = 0
            y += 2
        i += 1 
    im.save('qr.png')
    qrr = qrtools.QR()
    qrr.decode('qr.png')
    print qrr.data
    return qrr.data
host = "hack.bckdr.in"
port = 8010
tn = telnetlib.Telnet(host,port)
print tn.read_until('can')
i = 0
while True:
	i+=1
	print i
	data = tn.read_until('none',1)
	print data
	res = '0x'+getQR(data)
	kq = hex(int(res,16))
	kq = kq[2:-1]
	if len(kq) < 64:
		kq = '0'*(64-len(kq)) + kq
	tn.write(kq+"\n")