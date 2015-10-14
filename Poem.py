import sys
import itertools
from os import listdir
from os.path import isfile, join

abc='abcdefghijklmnopqrstuvwxyz'

def loadlist(infile):
	tlist = []
	for line in open(infile,'r'):
		for w in line.split(): tlist.append(w.lower())
	return tlist

def encrypt(code, poem, msg):
	# Load all words of the poem into a temporary list
	twords = loadlist(poem)

	# Select only those words specified in the code in a new list
	pwords = ''
	for c in code: pwords += twords[c].lower()
	plen = len(pwords)

	# We can only support encoding all alphabetical letters, a key length greater len(abc) is not reasonable here
	if plen > len(abc): sys.exit(3)

	# Assign an index for each letter in the key based on the alphabet
	pcode = [None] * plen
	count = 0
	while(count<plen):
		for al in abc:
			for pc, pl in enumerate(pwords):
				if al!=pl: continue
				pcode[pc]=count
				count+=1

	# Load all words of the message into a string
	mwords = ''
	for line in open(msg, 'r'):
		for w in line.split(): mwords+=w.lower()
	mlen = len(mwords)

	# Split message into chunks of size plen, append random (here alphabet) characters to fill the last chunk, if necessary
	cpairs = []
	curlen = plen
	while(curlen<mlen):
		cpairs.append(mwords[curlen-plen:curlen])
		curlen+=plen
	rword = mwords[curlen-plen:curlen]
	rlen = len(rword)
	if rlen < plen: rword += abc[:plen-rlen]
	cpairs.append(rword)

	# Encrypt the message according to the key
	cip = ''
	for i in code: cip+=abc[i]
	cip+=' '
	for i in pcode:
		for pair in cpairs:
			cip += pair[i]
		cip+=' '
	return cip

def decrypt(poem, cip):
	# Load all words of the poem into a temporary list
	twords = loadlist(poem)

	# Load all cipher chunks of the ciphertext into a list
	cwords = loadlist(cip)

	# Get the code rom the first chunk and remove it from the ciphertext list
	code = []
	for i in cwords.pop(0):
		code.append(abc.index(i))
	
	# Select only those words specified in the code in a new multi-arrayed list
	xwords = [[] for x in range(len(code))]
	for xcount, c in enumerate(code):
		tlen = c
		while(c<len(twords)):
			xwords[xcount].append(twords[c].lower())
			c+=26

	# Get all possible combinations
	for comb in itertools.product(*xwords):
		pwords = ''
		for c in comb: pwords+=c
		plen = len(pwords)

		# Rearrange the chunks according to the key
		pcode = [None] * plen
		count = 0
		while(count<plen):
			for al in abc:
				for pc, pl in enumerate(pwords):
					if al!=pl: continue
					pcode[count]=cwords[pc]
					count+=1

		# Decrypt the ciphertext
		msg = ''
		wlen = len(pcode[0])
		for c in range(0, wlen):
			for word in pcode:
				msg+=word[c]
		print msg

# first argument = poem
# second argument = ciphertxt or msg
if len(sys.argv) != 3: sys.exit(2)

#print encrypt([0, 5, 13, 16, 19], sys.argv[1], sys.argv[2])
decrypt(sys.argv[1], sys.argv[2])

