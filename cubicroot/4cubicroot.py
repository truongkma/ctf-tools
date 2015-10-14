"""Python: Carpenter’s formula for roots of quartic polynomial x^4 + px^3 + qx^2 + rx + s"""
import math
import gmpy2
gmpy2.get_context().precision=5000
from cubicroot import *
def Carpenter(p, q,r, s):
	p = gmpy2.mpfr(p)
	q = gmpy2.mpfr(q)
	r = gmpy2.mpfr(r)
	s = gmpy2.mpfr(s)
	"""
	Solves for all roots of the quartic polynomial P(x) = x^4 + px^3 + qx^2 + rx + s.
	"""
	#print "@@@ inside Carpenter", p,q,r,s
	pby4 = p/4.0
	C = ((6 * pby4) - 3*p)*pby4 + q
	D = (((-4*pby4) + 3*p)*pby4 - 2*q)*pby4 + r
	E = (((pby4 - p)* pby4 + q)*pby4 - r)*pby4 + s
	#print "C, D, E=",C, D, E
	root = None
	for zero in polyCubicRoots(2*C, (C**2 - 4*E), -D**2):
		#print "zero = ", zero
		if type(zero)== type(gmpy2.mpfr(1.0)) and zero > 0.0:
		   root = zero
		   #print "found a positive root."
		   break
	if root == None:
		return None
	sqroot = gmpy2.sqrt(root)
	Q1 = -root/4.0 - C/2.0 - D/2.0 / sqroot
	Q2 = -root/4.0 - C/2.0 + D/2.0 / sqroot
	#print "Q1,Q2=", Q1, Q2
	sqy2 = sqroot/2.0
	if Q1 >= 0.0:
	   sqQ1 = gmpy2.sqrt(Q1)
	   z1 = sqy2 + sqQ1 -pby4
	   z2 = sqy2 - sqQ1 -pby4
	else:
	   sqQ1 = gmpy2.sqrt(-Q1)
	   z1 = (sqy2-pby4,   sqQ1)
	   z2 = (sqy2-pby4, - sqQ1)
	if Q2 >= 0.0:
	   sqQ2 = gmpy2.sqrt(Q2)
	   z3 = -sqy2 - sqQ2 -pby4
	   z4 = -sqy2 + sqQ2 -pby4
	else:
	   sqQ2 = gmpy2.sqrt(-Q2)
	   z3 = (-sqy2-pby4, sqQ2)
	   z4 = (-sqy2-pby4, -sqQ2)
	return (z1, z2,z3, z4)

def test():
        p = -26
        q = 163
        r = 510
        s = -5400
        roots = Carpenter(p,q,r,s)
        for i, root in enumerate(roots):
                print "i = ",i
                print "root = ",root
p= 0b10001110000110111100100111111000100111
q= 0b1110110010101000100001010011110000010100100010111011100111100011010001010101
r= 0b1010111100101001100011011101101000000110011010100010001010001100010000111001010011110111011000110010000110010001
s= 0b11000010011110000010000010000101010000011101100011101110110110011111000000001011001101111100111001111110001100100101101010011011011101110111001110101
 
A=[]
B=[]
C=[]
D=[s]
 
for i in range(0,3):
        A.append(p * (2**i))
        B.append(q * (2**i))
        C.append(r * (2**i))
 
for i in A:
        print "===================="
        for j in B:
                for k in C:
                        for l in D:
                                (x1, x2, x3, x4) = Carpenter(-i,j,-k,l)
                                # since sometimes the solution will consist of complex numbers, we'll just disregard those with a try-except
                                try:
                                        #approximate value of x1
                                        aprox = int(x1.__floor__())
                                        for step in range(0,10000):
                                                #try to the right
                                                if s % (aprox + step) == 0:
                                                        print aprox + step
                                                #and to the left
                                                if s % (aprox - step) == 0:
                                                        print aprox - step
                                except:
                                        pass


