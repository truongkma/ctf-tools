from Crypto.Cipher import AES
from Crypto.Util.strxor import strxor
import base64
import binascii
import challenge18
import itertools

strings = [
    b'SSBoYXZlIG1ldCB0aGVtIGF0IGNsb3NlIG9mIGRheQ==',
    b'Q29taW5nIHdpdGggdml2aWQgZmFjZXM=',
    b'RnJvbSBjb3VudGVyIG9yIGRlc2sgYW1vbmcgZ3JleQ==',
    b'RWlnaHRlZW50aC1jZW50dXJ5IGhvdXNlcy4=',
    b'SSBoYXZlIHBhc3NlZCB3aXRoIGEgbm9kIG9mIHRoZSBoZWFk',
    b'T3IgcG9saXRlIG1lYW5pbmdsZXNzIHdvcmRzLA==',
    b'T3IgaGF2ZSBsaW5nZXJlZCBhd2hpbGUgYW5kIHNhaWQ=',
    b'UG9saXRlIG1lYW5pbmdsZXNzIHdvcmRzLA==',
    b'QW5kIHRob3VnaHQgYmVmb3JlIEkgaGFkIGRvbmU=',
    b'T2YgYSBtb2NraW5nIHRhbGUgb3IgYSBnaWJl',
    b'VG8gcGxlYXNlIGEgY29tcGFuaW9u',
    b'QXJvdW5kIHRoZSBmaXJlIGF0IHRoZSBjbHViLA==',
    b'QmVpbmcgY2VydGFpbiB0aGF0IHRoZXkgYW5kIEk=',
    b'QnV0IGxpdmVkIHdoZXJlIG1vdGxleSBpcyB3b3JuOg==',
    b'QWxsIGNoYW5nZWQsIGNoYW5nZWQgdXR0ZXJseTo=',
    b'QSB0ZXJyaWJsZSBiZWF1dHkgaXMgYm9ybi4=',
    b'VGhhdCB3b21hbidzIGRheXMgd2VyZSBzcGVudA==',
    b'SW4gaWdub3JhbnQgZ29vZCB3aWxsLA==',
    b'SGVyIG5pZ2h0cyBpbiBhcmd1bWVudA==',
    b'VW50aWwgaGVyIHZvaWNlIGdyZXcgc2hyaWxsLg==',
    b'V2hhdCB2b2ljZSBtb3JlIHN3ZWV0IHRoYW4gaGVycw==',
    b'V2hlbiB5b3VuZyBhbmQgYmVhdXRpZnVsLA==',
    b'U2hlIHJvZGUgdG8gaGFycmllcnM/',
    b'VGhpcyBtYW4gaGFkIGtlcHQgYSBzY2hvb2w=',
    b'QW5kIHJvZGUgb3VyIHdpbmdlZCBob3JzZS4=',
    b'VGhpcyBvdGhlciBoaXMgaGVscGVyIGFuZCBmcmllbmQ=',
    b'V2FzIGNvbWluZyBpbnRvIGhpcyBmb3JjZTs=',
    b'SGUgbWlnaHQgaGF2ZSB3b24gZmFtZSBpbiB0aGUgZW5kLA==',
    b'U28gc2Vuc2l0aXZlIGhpcyBuYXR1cmUgc2VlbWVkLA==',
    b'U28gZGFyaW5nIGFuZCBzd2VldCBoaXMgdGhvdWdodC4=',
    b'VGhpcyBvdGhlciBtYW4gSSBoYWQgZHJlYW1lZA==',
    b'QSBkcnVua2VuLCB2YWluLWdsb3Jpb3VzIGxvdXQu',
    b'SGUgaGFkIGRvbmUgbW9zdCBiaXR0ZXIgd3Jvbmc=',
    b'VG8gc29tZSB3aG8gYXJlIG5lYXIgbXkgaGVhcnQs',
    b'WWV0IEkgbnVtYmVyIGhpbSBpbiB0aGUgc29uZzs=',
    b'SGUsIHRvbywgaGFzIHJlc2lnbmVkIGhpcyBwYXJ0',
    b'SW4gdGhlIGNhc3VhbCBjb21lZHk7',
    b'SGUsIHRvbywgaGFzIGJlZW4gY2hhbmdlZCBpbiBoaXMgdHVybiw=',
    b'VHJhbnNmb3JtZWQgdXR0ZXJseTo=',
    b'QSB0ZXJyaWJsZSBiZWF1dHkgaXMgYm9ybi4=',
]

# Generated randomly.
key = b'\xa3\xc9\xe7\xedmZU\x1e\xac\x15\xe2\xaf\xb4$\xa9{'

def encryptString(s):
    cipher = challenge18.CTR(AES.new(key, AES.MODE_ECB), 0)
    return cipher.encrypt(s)

encryptedStrings = [encryptString(base64.b64decode(s)) for s in strings]

def getPrintableKeyChar(encryptedStrings, i):
    for j in range(256):
        decrypted = [x[i] ^ j for x in encryptedStrings]
        if all([chr(x) in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ,' for x in decrypted]):
            yield j

def extendKey(k, ciphertext, guess):
    return k + bytes([guess[i] ^ ciphertext[len(k) + i] for i in range(len(guess))])

if __name__ == '__main__':
    ks = [getPrintableKeyChar(encryptedStrings, i) for i in range(10)]
    k = bytes(list(itertools.islice(itertools.product(*ks), 1))[0])
    k = extendKey(k, encryptedStrings[1], b'h ')
    k = extendKey(k, encryptedStrings[3], b'entury ')
    k = extendKey(k, encryptedStrings[5], b'ss ')
    k = extendKey(k, encryptedStrings[3], b'se')
    k = extendKey(k, encryptedStrings[5], b'rds')
    k = extendKey(k, encryptedStrings[0], b' ')
    k = extendKey(k, encryptedStrings[29], b'ght')
    k = extendKey(k, encryptedStrings[4], b' ')
    k = extendKey(k, encryptedStrings[27], b'd')
    k = extendKey(k, encryptedStrings[4], b'ead')
    k = extendKey(k, encryptedStrings[37], b'n,')
    kl = len(k)
    decrypted = [strxor(x[:kl], k[:len(x)]) + x[kl:] for x in encryptedStrings]
    for i in range(len(decrypted)):
        if decrypted[i] != base64.b64decode(strings[i]):
            raise Exception('Invalid decryption')
        print(decrypted[i])
