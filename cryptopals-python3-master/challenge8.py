import challenge4
import itertools

lines = challenge4.decodeLines('8.txt')

def score(x):
    k = 16
    blocks = [x[i:i+k] for i in range(0, len(x), k)]
    pairs = itertools.combinations(blocks, 2)
    same = 0
    count = 0
    for p in pairs:
        if p[0] == p[1]:
            same += 1
    return same

lineNumber = 1
for l in lines:
    if score(l) > 0:
        print(lineNumber)
    lineNumber += 1
