import binascii
import challenge31
import sys
import time

def guessNextByte(file, knownBytes, delay):
    suffixlen = 20 - len(knownBytes)
    start = time.perf_counter()

    durations = [0] * 256

    count = 10
    for k in range(count):
        for i in range(256):
            suffix = bytes([i]) + (b'\x00' * (suffixlen - 1))
            signature = knownBytes + suffix
            durations[i] += challenge31.isValidSignature(file, binascii.hexlify(signature).decode('ascii'))[1]

    end = time.perf_counter()
    print('Made {0} requests in {1:.2f}s; rps = {2:.2f}'.format(count * 256, end - start, count * 256 / (end - start)))

    for i in range(256):
        durations[i] /= count

    avg_duration = sum(durations) / 256
    argmax = max(range(256), key=lambda i: durations[i])

    if durations[argmax] > avg_duration + 0.80 * delay:
        return knownBytes + bytes([argmax])
    else:
        return knownBytes[:-1]

if __name__ == '__main__':
    file = sys.argv[1]
    knownBytes = b''
    DELAY = 0.005
    while True:
        if len(knownBytes) == 20:
            if challenge31.isValidSignature(file, binascii.hexlify(knownBytes).decode('ascii'))[0]:
                break
            else:
                knownBytes = knownBytes[:-1]
        knownBytes = guessNextByte(file, knownBytes, DELAY)
        print(binascii.hexlify(knownBytes))
    print(binascii.hexlify(knownBytes))
