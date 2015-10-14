import challenge52
import challenge53

def constructCollisionTree(hashFn, blockLength, hashLength, k):
    leaves = [(i.to_bytes(hashLength, byteorder='little'),)
              for i in range(2**k)]

    initialStateMap = {leaves[i][0]:i for i in range(2**k)}

    collisionTree = [leaves]

    for i in range(1, k+1):
        prev_level = collisionTree[i-1]
        curr_level = [
            challenge53.findStatePrefixCollision(hashFn, prev_level[2*i][0], prev_level[2*i+1][0], blockLength) for i in range(2**(k-i))]
        collisionTree += [curr_level]

    return (initialStateMap, collisionTree)

def getSuffixFromCollisionTree(initialStateMap, collisionTree, iv):
    s = b''
    k = len(initialStateMap).bit_length() - 1

    i = initialStateMap[iv]
    for j in range(1, k+1):
        n = collisionTree[j][i//2]
        s += n[1 + (i%2)]
        i //= 2
    return s

def generatePrediction(hashFn, padFn, initialStateMap, collisionTree, messageLength, blockLength):
    k = len(initialStateMap).bit_length() - 1
    totalBlockLength = (messageLength + (blockLength - 1)) // blockLength
    # One glue block, plus k for the suffix.
    totalBlockLength += k + 1
    totalLength = totalBlockLength * blockLength
    return hashFn(padFn(b'', totalLength), collisionTree[-1][0][0], pad=False)

def forgePrediction(hashFn, iv, padFn, initialStateMap, collisionTree, messageLength, blockLength, m):
    if len(m) > messageLength:
        raise Exception('message too big')
    paddedMessageLength = messageLength + (-messageLength % blockLength)
    m += b'\x00' * (paddedMessageLength - len(m))
    h = hashFn(m, iv, pad=False)

    glue, h = challenge53.findCollisionInSet(hashFn, h, blockLength, initialStateMap)
    m += glue
    suffix = getSuffixFromCollisionTree(initialStateMap, collisionTree, h)
    m += suffix

    return m

if __name__ == '__main__':
    k = 5
    messageLength = 100
    (initialStateMap, collisionTree) = constructCollisionTree(challenge52.badHash, challenge52.badHashBlockLength, challenge52.badHashHashLength, k)
    prediction = generatePrediction(challenge52.badHash, challenge52.badHashPadMessage, initialStateMap, collisionTree, messageLength, challenge52.badHashBlockLength)

    print('Prediction', prediction)

    forgedPrediction = b'Dodgers win the World Series!!'
    forgedPredictionMessage = forgePrediction(challenge52.badHash, b'', challenge52.badHashPadMessage, initialStateMap, collisionTree, messageLength, challenge52.badHashBlockLength, forgedPrediction)
    h = challenge52.badHash(forgedPredictionMessage, b'')
    print('Forged prediction', forgedPredictionMessage, h)
