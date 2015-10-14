#!/usr/bin/python
import ContinuedFractions
import Arithmetic
import time
import sys
import base64
import binascii
import gmpy
import sympy
import math
import fractions
import struct
sys.setrecursionlimit(100000)


def hack_RSA(e, n):
    print "Hacking"
    frac = ContinuedFractions.rational_to_contfrac(e, n)
    convergents = ContinuedFractions.convergents_from_contfrac(frac)
    for (k, d) in convergents:
        if k != 0 and (e * d - 1) % k == 0:
            phi = (e * d - 1) // k
            s = n - phi + 1
            discr = s * s - 4 * n
            if(discr >= 0):
                t = Arithmetic.is_perfect_square(discr)
                if t != -1 and (s + t) % 2 == 0:
                    print "done"
                    print d
                    return d

e = 2385330119331689083455211591182934261439999376616463648565178544704114285540523381214630503109888606012730471130911882799269407391377516911847608047728411508873523338260985637241587680601172666919944195740711767256695758337633401530723721692604012809476068197687643054238649174648923555374972384090471828019
n = 2562256018798982275495595589518163432372017502243601864658538274705537914483947807120783733766118553254101235396521540936164219440561532997119915510314638089613615679231310858594698461124636943528101265406967445593951653796041336078776455339658353436309933716631455967769429086442266084993673779546522240901
print hack_RSA(e, n)
