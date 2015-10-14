from Crypto.PublicKey import RSA
def getPrivate(n, e, p, q):
	d = modInv(e, (p-1)*(q-1))
	return RSA.construct((n, e, d, p, q, ))
def modInv(a, m):
	g, x, y = egcd(a, m)
	if (g != 1):
		raise Exception("[-]No modular multiplicative inverse of %d under modulus %d" % (a, m))
	else:
		return x % m
def egcd(a, b):
	if (a == 0):
		return (b, 0, 1)
	else:
		g, y, x = egcd(b % a, a)
		return (g, x - (b // a) * y, y)

p = (pow(2, 2281)-1)
q = (pow(2, 2203)-1)
pubKey = RSA.importKey(open("pub.pub", 'rb').read())
privKey = getPrivate(pubKey.n, pubKey.e, p, q)
print pubKey.n

