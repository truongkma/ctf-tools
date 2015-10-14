# from PIL import Image
# #import subprocess
# from pytesser import *
# import os
# filename = '0000'
# PNG_PATH='/home/truongkma/Desktop/write-ups-2015-master/volgactf-quals-2015/stego/captcha/output/png/'
# png = [ f for f in os.listdir(PNG_PATH) if os.path.isfile(os.path.join(PNG_PATH, f)) ]
# png.sort()
# im = Image.open(PNG_PATH+'00000001.png')
# im.save('a.tif')
# im = Image.open('a.tif')
# print image_to_string(im)
# #print png
# #a = ''
# #for i in png:
# #	print PNG_PATH+i
# #	im = Image.open(PNG_PATH+i)
# 	#im.save('a.tif')
# 	#im = Image.open('a.tif')
# #	a += image_to_string(im)
# #	print a
#!/usr/bin/python

from pytesser import *
import os
import Image
import subprocess

PNG_PATH='/home/truongkma/Desktop/write-ups-2015-master/volgactf-quals-2015/stego/captcha/output/png/'

pngfiles = [ f for f in os.listdir(PNG_PATH) if os.path.isfile(os.path.join(PNG_PATH, f)) ]
pngfiles.sort()
flag = ""
print "[+] Processing image files ..."
for f in pngfiles:
 im = Image.open(PNG_PATH + f)
 flag += image_to_string(im)

flag = "".join(flag.split())
print "[+] Encoded flag is: " + flag 