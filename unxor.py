#!/usr/bin/env python

import os
import re
import math
import argparse
import logging
import sys
import itertools

"""

unXOR
===========

This tool will search through an XOR-encoded file (binary, text-file, whatever) and use known-plaintext attacks to deduce the original keystream. Works on keys half as long as the known-plaintext, in linear complexity.

The code is pretty straightforward

For more details and a short explanation of the theory behind this, please refer to:

 - My original blogpost: http://tomchop.me/2012/12/yo-dawg-i-heard-you-like-xoring/
 - The insipiring post: http://playingwithothers.com/2012/12/20/decoding-xor-shellcode-without-a-key/

Related work:

 - Didier Steven's XORsearch : http://blog.didierstevens.com/programs/xorsearch/

Written by Thomas Chopitea (@tomchop_)

"""

# quick shannon-entropy calculation
def H(data):
  	h = 0
	entropy = 0
	for x in range(256):
		p_x = float(data.count(chr(x)))/float(len(data))
		#print p_x
		if p_x > 0:
			entropy -= p_x * math.log(p_x,2)
	return entropy


# generate key from bytes
def genkey(key, keylen):
	repeat = ""
	key = key.decode('hex')
	while (len(repeat) < keylen):
		repeat += key
	return repeat[:keylen]

# easier this way
def xor(plaintext, key):
	return "".join(chr(ord(p)^ord(k)) for p, k in zip(plaintext, key))

def xor_full(plaintext, key):
	return "".join(chr(ord(p)^ord(k)) for p, k in zip(plaintext, itertools.cycle(key)))

# we reduce the problem to single-byte key search by selecting every other nth byte from the cyphertext and the known-plaintext
def selective(crypt, search):

	keylen = 1
	find = False
	decryptions = []
	keys = []

	while keylen < len(search) and not find:
		sel_crypt = crypt[::keylen]
		sel_search = search[::keylen]

		norm_crypt = xor(sel_crypt,sel_crypt[1:])
		norm_search = xor(sel_search,sel_search[1:])

		if len(norm_search) > 0:

			logging.info("[*] Trying key length %s" % keylen)
			logging.debug("================================================================")
			logging.debug("Crypt:\t\t %s" % " ".join(a.encode('hex') for a in crypt))
			logging.debug("Norm_crypt:\t %s" % " ".join(a.encode('hex') for a in norm_crypt)) 
			logging.debug("Norm_search:\t %s" % " ".join(a.encode('hex') for a in norm_search))
			logging.debug("================================================================")

			indexes = [m.start() for m in re.finditer(re.escape(norm_search), norm_crypt)]


			offset = 0
			# we haven't found the normalized search, so let's try using an offset
			while offset < keylen and len(indexes) == 0 and len(norm_search) > 0:
					offset += 1
					logging.debug("Offset: %s", offset)
					
					sel_crypt = crypt[offset::keylen]
					norm_crypt = xor(sel_crypt,sel_crypt[1:])

					
					if len(norm_search) > 0:
						indexes = [m.start() for m in re.finditer(re.escape(norm_search), norm_crypt)]

			# something was found
			if len(indexes) > 0:

				for index in indexes:
					logging.debug("[*] Search term (%s) found at %s (%s in the cyphertext)" % ("^".join(sel_search), index, index*keylen+offset))

					keystr_guess = sel_crypt[index:index+len(norm_search)]	
					
					keystr_guess = xor(keystr_guess, sel_search)[:1]
					logging.debug("(%s, %s)" %(keystr_guess, keystr_guess.encode('hex')))
					
					# we have to 'expand' the partial keystream found to the original keylength
					long_key = ""
					long_plaintext = ""
					
					# we assume that the place where our symbol was found is the start of the search string
					# this may or may not be a coincidence

					for i in range(keylen):
						if (index*keylen+i+offset) < len(crypt):
							if i % keylen == 0:
								long_key += keystr_guess
							else:
								long_key += chr(ord(search[i])^ord(crypt[index*keylen+i+offset]))
							
					if long_key != "":
						long_key = long_key[-(offset % keylen):] + long_key[:-(offset % keylen)]

						logging.info("[*] Keystream guess: %s" % (long_key.encode('hex')))
						decrypt = xor(crypt, genkey(long_key.encode('hex'), len(crypt)))

						if decrypt.find(search) != -1:
							find = True
							if long_key not in keys:
								decryptions.append(decrypt)
								keys.append(long_key)
						else:
							keylen += 1

			else:
				keylen += 1
	return decryptions, keys


def iterative(crypt, search, once=False):
	
	norm_crypt = crypt
	norm_search = search
	i = 0
	find = False
	decryptions = []
	keys = []

	# keep normalizing as much as possible
	while len(norm_search) > 0 and not find:
		i += 1

		# normalization process happens here
		norm_crypt = xor(norm_crypt,crypt[i:])
		norm_search = xor(norm_search,search[i:])

		if i % 2 == 1 and len(norm_search) > 0:
			keylen = (i/2 + 1)

			# print info
			logging.info("[*] Trying key length %s" % keylen)
			logging.debug("="*64)
			logging.debug("Crypt:\t\t %s" % " ".join(a.encode('hex') for a in crypt))
			logging.debug("Norm:\t\t %s" % " ".join(a.encode('hex') for a in norm_crypt)) 
			logging.debug("Norm_search:\t %s" % " ".join(a.encode('hex') for a in norm_search))
			logging.debug("="*64)

			# gather all indexes where an occurrence of norm_search is found in norm_crypt
			# means that search is in crypt at the same index
			indexes = [m.start() for m in re.finditer(re.escape(norm_search), norm_crypt)]

			# check if we have search results
			if len(indexes) > 0:
				logging.debug("[!] One or more occurences of the search string found. Some might be coincidence, some might not.")
				logging.debug("[!] String found at %s" % ", ".join(str(a) for a in indexes))

				# cycle through search results
				for index in indexes:
					logging.debug("\n[*] Search term found at %s " % index)

					# guessing keystream from index to index+len(norm_search)
					keystr_guess = crypt[index:index+len(norm_search)]
					# crypt ^ plaintext = keystream
					keystr_guess = xor(keystr_guess,search)
					# first keystream guess
					keystr_guess = keystr_guess[:keylen]
					
					if len(norm_search) < keylen:
						logging.info("[.] Normalized search (%s) is shorter than key length (%s)" % (len(norm_search), keylen))
						logging.info("[.] This might be a false positive")
					logging.info("[*] Keystream guess: %s" % keystr_guess.encode('hex'))
					
					# recover the actual key from the keystream guess - many decryptions and keys possible
					decrypt, key = recover_key(crypt,keystr_guess,keylen,index,search)
					
					# check if the plaintext is found in the decrypted text
					if decrypt.find(search) != -1:
						logging.info("[*] Recovered key: %s" % key[:keylen].encode('hex'))
						find = True
						if key not in keys:
							keys.append(key)
							decryptions.append(decrypt)
					else:
						logging.info("[x] Invalid key")

			# we don't have any search results
			else:
				logging.info("[!] Search term not found. Increasing norm level / key length.")
			# ?
			if once:
				return None, None

	# we seem to have a valid decryption
	if find:
		return decryptions, keys
	
	# no valid encryption found 
	elif len(norm_search) == 0: 
		logging.info("[!] Normalization level too high given the length of the known plaintext. Try again with a longer known plaintext.")
		return None, None
			


def recover_key(crypt, keystr_guess, keylen, index, search):

	partial = False
	
	# this means we haven't found the whole key, some bytes are missing
	if len(keystr_guess) < keylen:
		partial = True

	decrypt = xor(crypt, keystr_guess+"\x00")

	if len(keystr_guess) < keylen:
		logging.info("[?] Some bytes of the key are missing, taking a wild guess (assuming findings ~ search query)")
		logging.info("[?] If results don't make sense, try searching for something with less entropy (e.g. URLs), or use a longer search string")
	
	while len(keystr_guess) < keylen:
		# we take a wild guess, and suppose the keystream guess was found 
		# because of an occurrence of our search term in the plaintext
		findings = decrypt.find(search[:(index%len(keystr_guess))])
		keystr_guess += chr(ord(crypt[index+len(keystr_guess)])^ord(search[len(keystr_guess)]))

	# get the correct start of the keystream	
	key = keystr_guess[-(index % keylen):]
	key += keystr_guess[:-(index % keylen)]

	# repeat key as long as it's needed
	while len(key) < len(crypt):
		key += key

	decrypt = xor(crypt,key)
	
	return decrypt, key[:keylen]


def decryption(crypt, search, method, debug=False):

		if debug:
			logging.basicConfig(level=logging.DEBUG, format="%(message)s")


		if method == "iterative":
			decrypt, key = iterative(crypt, search)

		if method == "selective":
			decrypt, key = selective(crypt, search)

		return decrypt, key


if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="Decode XOR-encoded files. Can try guessing keys using known-plaintext attacks.")
	
	mutex = parser.add_mutually_exclusive_group(required=True)
	mutex.add_argument("-g", "--guess", help="Search string to use when trying known-plaintext attacks")
	mutex.add_argument("-k", "--key", help="The XOR key (hex)")

	guess = parser.add_argument_group(title='Unknown key')
	guess.add_argument("-m","--method", choices=['iterative','selective'], default="iterative", help='Use iterative or selective (experimental) method')
	guess.add_argument("-x", "--hex", help="Search in hex", action="store_true")
	
	parser.add_argument("infile", nargs="?", help="The file to read from", type=argparse.FileType("r"), default=sys.stdin)
	parser.add_argument("outfile", nargs="?", help="The dump file", type=argparse.FileType('w'), default=sys.stdout)
	parser.add_argument("-v", "--verbose", help="Verbose output", type=int, choices=[0,1,2], default=0)
	
	args = parser.parse_args()
	infile = args.infile
	outfile = args.outfile

	if args.verbose == 1:
		logging.basicConfig(level=logging.INFO, format="%(message)s")
	if args.verbose == 2:
		logging.basicConfig(level=logging.DEBUG, format="%(message)s")


	if args.key:
		if not re.match("^([a-fA-F0-9]{2,2})+$",args.key):
			print "The key must be given in hex (e.g. FF00FF00)"
			exit()
		crypt = infile.read()
		key = genkey(args.key,len(crypt))

		outfile.write(xor(crypt,key))


	if args.guess:

		crypt = infile.read()
		search = args.guess

		# some quick stats
		logging.info( "\nStats ========================")
		logging.info( "Encrypted data length:\t%s" % len(crypt))
		logging.info( "Search string length:\t%s" % len(search))
		logging.info( "Encrypted data entropy:\t%s" % H(crypt))
		logging.info( "Search string entropy:\t%s" % H(search))
		logging.info( "==============================\n")

		decrypt, key = decryption(crypt, search, args.method)

		if not decrypt and not key:
			exit()

		for i in range(len(decrypt)):
			d = decrypt[i]
			k = key[i]
			if args.verbose > 0:
				outfile.write("Decryption attempt (key: 0x%s)\n%s\n" % (k.encode('hex'), d))
			else:
				outfile.write(d)
			if args.verbose > 0:
				outfile.write("\n")



		

