import util

if __name__ == '__main__':
    x = b'YELLOW SUBMARINE'
    expectedY = b'YELLOW SUBMARINE\x04\x04\x04\x04'
    y = util.padPKCS7(x, 20)
    print(y)
    print(expectedY)
    if y != expectedY:
        raise Exception(y + b' != ' + expectedY)
