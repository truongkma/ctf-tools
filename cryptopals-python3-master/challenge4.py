import binascii
import challenge3

def decodeLines(filename):
    f = open(filename, 'r')
    for line in f:
        if line[-1] == '\n':
            line = line[:-1]
        s = binascii.unhexlify(line)
        yield s

def findSingleByteXOR(lines):
    brokenLines = [challenge3.breakSingleByteXOR(l)[1] for l in lines]
    def score(i):
        return challenge3.score(brokenLines[i])
    maxI = max(range(len(brokenLines)), key=score)
    return (maxI+1, brokenLines[maxI])

if __name__ == '__main__':
    print(findSingleByteXOR(decodeLines('4.txt')))
