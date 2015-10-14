#!/usr/bin/python
from subprocess import *
import commands
import socket


def horosho(s):
    i = s.find('\\x')
    res = s[0:i]
    while i != -1:
        n = int(s[i + 2:i + 4], 16)
        res += chr(n)
        s = s[i + 4:]
        i = s.find('\\x')
    res += s
    return res
digest = 'b34c39b9e83f0e965cf392831b3d71b8'
data = '\'do test connection\''
addData = 'give'
length = 5
for length in xrange(1, 257, 1):
    args = '-s ' + digest + ' --data ' + data + ' -a ' + \
        addData + ' -k ' + str(length) + ' > file'
    output = commands.getstatusoutput('hashpump ' + args)
    payload = open('file', 'rb').read()
    payload = payload[:-1]
    payload = payload[0:32] + ' ' + payload[33:]
    payload = horosho(payload)
