#! /usr/bin/env python

def score(string):
  freq = dict()
  freq['a']=834
  freq['b']=154
  freq['c']=273
  freq['d']=414
  freq['e']=1260
  freq['f']=203
  freq['g']=192
  freq['h']=611
  freq['i']=671
  freq['j']=23
  freq['k']=87
  freq['l']=424
  freq['m']=253
  freq['n']=680
  freq['o']=770
  freq['p']=166
  freq['q']=9
  freq['r']=568
  freq['s']=611
  freq['t']=937
  freq['u']=285
  freq['v']=106
  freq['w']=234
  freq['x']=20
  freq['y']=204
  freq['z']=6
  freq[' ']=2320

  ret = 0

  for c in string.lower():
    if c in freq:
      ret += freq[c]

  return ret

def xor_data(A, B):
  return ''.join(chr(ord(A[i])^ord(B[i])) for i in range(len(A)))

def single_xor(string, key):
  return xor_data(string, key*len(string))

def is_printable(data):
  from string import printable
  return all(d in printable for d in data)

def get_choices_for_single_xor(data):
  if type(data) == list:
    if type(data[0]) == int:
      data = [chr(d) for d in data]
    data = ''.join(data)
  choices = sorted(range(256), key=lambda i: score(single_xor(data,chr(i))))[::-1]
  return [c for c in choices if is_printable(single_xor(data,chr(c)))]

def crack_single_xor(data):
  return chr(get_choices_for_single_xor(data)[0])

if __name__ == '__main__':
  data = 'hello this is sparta enter the element'
  key = crack_single_xor(data)
  if key == '\x00':
    print "[+] NO-XOR test passed"
    print "    [-] Decoded: %s" % repr(single_xor(data,key))
  else:
    print "[-] NO-XOR test failed. Gave %s instead." % repr(key)
    print "    [-] Decoded: %s" % repr(single_xor(data,key))

  data = single_xor(data,'a')
  key = crack_single_xor(data)[0]
  if key == 'a':
    print "[+] key=='A' test passed"
    print "    [-] Decoded: %s" % repr(single_xor(data,key))
  else:
    print "[-] key=='A' test failed. Gave %s instead." % repr(key)
    print "    [-] Decoded: %s" % repr(single_xor(data,key))
