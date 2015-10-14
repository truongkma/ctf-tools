# Written By H4rryp0tt3r
from PIL import Image
im = Image.open('stego200.png', 'r')
pix = im.getdata()
bins = ""
outfile = open("steg.rar", "ab")
for i in pix:
    bins += bin(i)[-1]
for j in range(0, len(bins), 8):
    outfile.write(chr(int(bins[j:j + 8], 2)))
