import gmpy
import requests
url = 'http://task.yeuchimse.com/5da027269cbcff2c24511e43305e6adf/?answer='
r = requests.get(url)
ck = {'PHPSESSID': r.cookies['PHPSESSID']}
# print r.headers
print ck
r = requests.get(url, cookies=ck)
code = r.text.splitfi('<code>')[1].split('</code>')[0]
lv = 0
try:
    while int(code):
        yn = ('YES' if gmpy.is_prime(int(code)) else 'NO')
        r = requests.get(url + yn, cookies=ck)
        print '[+] Lv :', lv, yn
        code = r.text.split('<code>')[1].split('</code>')[0]
        lv = r.text.split('content: "Level ')[1].split('"')[0]
except:
    print '[+] We got:', code
