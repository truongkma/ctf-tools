import base64
import challenge3
import challenge5
import itertools

def getHammingDistance(x, y):
    return sum([bin(x[i] ^ y[i]).count('1') for i in range(len(x))])

x = b'this is a test'
y = b'wokka wokka!!!'
expectedD = 37
d = getHammingDistance(x, y)
if d != expectedD:
    raise Exception(encodedD + ' != ' + encodedExpectedD)

#x = base64.b64decode(open('6.txt', 'r').read())
x = '0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0d0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a0a620f030c621b0d176201030c62060701101b1216620362110b0c050e0762001b1607623a2d3062272c21303b32362726622f273131232527636363636363636363636363636363636362242e2325393a72301d2e2b29711d362a7130711d2b661d2c721d36722f2d30302d353f'.decode('hex')

def breakRepeatingKeyXor(x, k):
    blocks = [x[i:i+k] for i in range(0, len(x), k)]
    transposedBlocks = list(itertools.zip_longest(*blocks, fillvalue=0))
    key = [challenge3.breakSingleByteXOR(bytes(x))[0] for x in transposedBlocks]
    return bytes(key)

def normalizedEditDistance(x, k):
    blocks = [x[i:i+k] for i in range(0, len(x), k)][0:4]
    pairs = list(itertools.combinations(blocks, 2))
    scores = [getHammingDistance(p[0], p[1])/float(k) for p in pairs][0:6]
    return sum(scores) / len(scores)

k = min(range(2, 41), key=lambda k: normalizedEditDistance(x, k))

key = breakRepeatingKeyXor(x, k)
y = challenge5.encodeRepeatingKeyXor(x, key)
print(key, y)
