from PIL import Image
import gmpy
import requests
from pytesser import *
import re
import urllib
import urllib2
url = 'http://ctf.framgia.vn:1990/index'
session = requests.Session()
response = session.get(url)
x = session.cookies.get_dict()
cookie = {'ss_sign': '04e46995e0ff0150aaf93fe0136b16ec', 'ss_user_id': '216',
          'ss_user_name': 'KevinKien', 'ss_team_name': '"X Hunt3r"',
          'session': '.eJw9zkELgjAYgOG_Et-5Q1vWQfAwWIqHTRQLvl2EbLI2KphKOPG_Jx66voeHd4am87o3EA9-1Htong-IZ9jdIYaivjlp2VFxFpRlkQjpq-CCrt1gXRllr0Ra6QRvE1j20Pa-a4aP0-8_IbP8gME4SZFgaCdlU1Nwdlq5SQRlkOaRyC4EafnFUDnJkYoy2bix137bAUrOsPwAKUQ1wQ.CJ47wA.V4iteUJk0LmHor3lBv17zFXysqc'}
while True:
    r = requests.get(url, cookies=cookie)
    #	code = 'http://ctf.framgia.vn:1990/static/00f88fa0-3835-11e5-b05a-de589671ad0a.png'
    code = r.text.split('src="')[3].split('"')[0]
    code = "http://ctf.framgia.vn:1990" + code
    urllib.urlretrieve(code, '1.png')
    im = Image.open('1.png')
    im.save('11.tif')
    im = Image.open('11.tif')
    p = image_to_string(im)
    print p
    number = re.findall('\d+', p)
    # print number[0],number[1]
    if '*' in p:
        kq = int(number[0]) * int(number[1])
    if 'mul' in p:
        kq = int(number[0]) * int(number[1])
    if 'mu|' in p:
        kq = int(number[0]) * int(number[1])
    if 'A' in p:
        kq = int(number[0]) ^ int(number[1])
    if 'xor' in p:
        kq = int(number[0]) ^ int(number[1])
    if '&' in p:
        kq = int(number[0]) & int(number[1])
    if 'and' in p:
        kq = int(number[0]) & int(number[1])
    if 'or' in p:
        kq = int(number[0]) | int(number[1])
    if '|' in p:
        if 'mu' in p:
            kq = int(number[0]) * int(number[1])
        else:
            kq = int(number[0]) | int(number[1])
    if '+' in p:
        kq = int(number[0]) + int(number[1])
    if 'plus' in p:
        kq = int(number[0]) + int(number[1])
    if 'mod' in p:
        kq = int(number[0]) % int(number[1])
    if '%' in p:
        kq = int(number[0]) % int(number[1])
    if '-' in p:
        kq = int(number[0]) - int(number[1])
    if 'minus' in p:
        kq = int(number[0]) - int(number[1])

    print kq
    payload = {'result': kq}
    r = requests.post(url, cookies=cookie, data=payload)
    if 'flag{' in r.text:
        print r.text
