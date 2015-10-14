from PIL import Image
 
img = Image.open("tumblr_m56lklxhkn1r0opwzo1_500.jpg")
img2 = Image.open("ngu.png")
pix = img.load()
pix2 = img2.load()
for i in xrange(img.size[0]):
  for j in xrange(img.size[1]):
    if pix[i,j]!=pix2[i,j]:
      pix2[i,j]=(0,0,0)
    else:
      pix2[i,j]=(255,255,255)
 
img2.save("result.jpg")
