from PIL import Image
from pytesser import image_to_string
im = Image.open('abc.png')
# im.save('11.tif')
# im = Image.open('11.tif')
p = image_to_string(im)
print p
