"""Python: Roots of the cubic polynomial P(x) =x^3 + ax^2 + bx + c"""
from math import *
def cuberoot(x):
    if x>=0:
        return x**(1/3.0)
    else:
        return -(-x)**(1/3.0)
def polyCubicRoots(a,b,c):
    #print "input=", a,b,c
    aby3 = a / 3.0
    p = b - a*aby3
    q = (2*aby3**2- b)*(aby3) + c
    X =(p/3.0)**3
    Y = (q/2.0)**2
    Q = X + Y
    #print "Q=", Q
    if Q >= 0:
        sqQ = sqrt(Q)
        t = (-q/2.0 + sqQ)
        A = cuberoot(t)
        t = (-q/2.0 - sqQ)   
        B = cuberoot(t)
        r1 = A + B - aby3
        re = -(A+B)/2.0-aby3
        im = sqrt(3.0)/2.0*(A-B)
        r2 = (re,im)
        r3 = (re,im)
    else:
        p3by27 = sqrt (-p**3/27.0)
        costheta = -q/2.0/p3by27
        #print "@@@ costheta= ",costheta
        alpha = acos(costheta)
        mag = 2 * sqrt(-p/3.0)
        alphaby3 = alpha/3.0
        r1 = mag * cos(alphaby3) - aby3
        r2 = -mag * cos(alphaby3 + pi/3) - aby3
        r3 = -mag * cos(alphaby3 - pi/3) - aby3
    return r1,r2,r3
def test():
    print "case 1: three different real roots."
    p,q,r = -31,318,-1080
    print "p,q,r = ",p,q,r
    for i,r in enumerate(polyCubicRoots(p,q,r)):
        print i+1,r
    print
    print "Case 2:Three real roots, two equal."
    p,q,r = -4, -51, -90
    print "p,q,r = ", p, q, r
    for i, r in enumerate(polyCubicRoots(p,q,r)):
        print i+1,r
    print
    print "Case 3:Two complex conjugate roots. One real root."
    p,q,r = -14, 53, -130
    print "p,q,r = ", p, q, r
    for i, r in enumerate(polyCubicRoots(p,q,r)):
        print i+1, r
    print
    p,q,r=0, -1.4, 3.861
    print "Case 4: contributed by anon."
    print "p,q,r = ", p, q, r
    for i, r in enumerate(polyCubicRoots(p,q,r)):
        print i+1,r
    print
test()