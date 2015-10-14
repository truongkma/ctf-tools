#!/usr/bin/env python
# encoding: utf-8
"""
exercises.py

Created by Daniel O'Donovan on 2008-09-17.
Copyright (c) 2008 University of Cambridge. All rights reserved.
"""
import sys
sys.path.append( '/Users/djo35/Code/bnn/py' )
sys.path.append( '/Users/indiedan/Code/bnn/py' )
sys.path.append( '/home/indiedan/Code/bnn/py' )
import ggplot
# import gmpy
#import numpy
import math

def fact(x): return (1 if x==0 else x * fact(x-1))

def Alg_121( n, verbose=False ):
    """ The Sieve of Eratosthenes """
    int_list = numpy.arange(2, n)
    for i in int_list:
        if i == 0: continue
        for jj, j in enumerate( int_list ):
            if j == 0 or i == j: continue
            if j % i == 0: 
                int_list[jj] = 0
        # if we've got this far i is prime
    prime_list = []
    for i in int_list:
        if i:
            if verbose: 
                print ' %d ' % (i),
            prime_list.append( i )
    return prime_list

def Alg_Euclid(a, b, verbose=False):
    """ Euclid's Algorithm p 34  (for gcd) """
    if a < b: a, b = b, a
    if a % b == 0: return b
    #print a, b
    while a != b:
        if a > b:
            a = a - b
        else:
            b = b - a
    return a

def Alg_improved_Euclid( a, b ):
    """ Simple recursive implementation (for gcd) """
    if a < b: a, b = b, a
    if a % b == 0: return b
    #print a, b
    if b == 0: return a
    else: return Alg_improved_Euclid( b, a % b )

def Alg_122( N, maxq=8 ):
    """ Continued Fraction Algorithm """
    qs = []
    xs = []
    
    xs.append( math.sqrt( N ) )
    qs.append( int( math.sqrt( N ) ) )

    for i in range( maxq ):
        xs.append( 1.0 / (xs[-1] - qs[-1]) )
        qs.append( int( xs[-1] ) )
    return qs

def find_order( a, n, verbose=True ):
    if Alg_Euclid( a, n ) != 1:
        if verbose:
            print '%d and %d not co-prime' % (a, n)
        return
    def func( a, r, n ): return gmpy.mpz(a ** r) % n
    for i in range( 1, n+1 ):
        if verbose:
            print i, func( a, i, n )
        if func( a, i, n ) == 1:
            if verbose:
                print 'The order of %d modulo %d is %d' % (a, n, i)
            return i
    print 'Cannot find order'
    return 0

def totient(n): 
    """ 
    count totatives of n, assuming gcd already 
    defined 
    """ 
    if not (type(n)==type(1) and n>=0): 
        raise ValueError, 'Invalid input type' 
    tot,pos = 1, n-1   
    while pos>1: 
       if Alg_improved_Euclid(pos,n)==1: tot += 1 
       pos -= 1 
    return tot


def find_primitive_roots( n, tot_n=None ):
    """ for exercise 1.6.4 """
    if not tot_n:
        tot_n = totient( n )
    for i in range( 1, n ):
        order = find_order( i, n, verbose=False )
        if order:
            if tot_n == order:
                print '%d is a primitive root of %d' % (i, n)

def find_lam( x1, y1, x2, y2, a, N ): 
    if (x1 == x2) and (y1 == y2): 
        return ( (( 3 * (x1 ** 2) + a) % N) / ((2 * y1) % N) )
    else:
        if (x2 - x1) == 0:
            print 'Have reached OE'
            sys.exit()
        return ((y2 - y1) / (x2 - x1)) % N
def update_x( lam, x1, x2, N ): return (( lam ** 2 - x1 - x2) % N)
def update_y( lam, x1, x3, y1, N ): return (( lam * (x1 - x3) - y1) % N)

def exercise_172( x1, y1, a, b, N, k ):
    x2, y2 = x1, y1
    for i in range( 1, k + 1 ):
        lam = find_lam( x1, y1, x2, y2, a, N )
        x3 = update_x( lam, x1, x2, N) % N
        y3 = update_y( lam, x1, x3, y1, N) % N
        print '( %2d, %2d ) (+) ( %2d, %2d ) = %4dP ( %2d, %2d ) mod %2d' % (x1, y1, x2, y2, i, x3, y3, N)
        x2, y2 = x3, y3

def int2bin( n ):
    '''convert denary integer n to binary string bStr'''
    bStr = ''
    if n < 0:  raise ValueError, "must be a positive integer"
    if n == 0: return '0'
    while n > 0:
        bStr = str(n % 2) + bStr
        n = n >> 1
    return bStr

def FastModExp_01( x, e, n ):
    """ calculate x^e mod n as per alg. 2.1.1 """
    eb = int2bin( e )
    beta = len( eb )
    c = 1
    # for i in range( beta - 1, -1, -1):
    for i in range( beta ):
        c = c ** 2 % n
        if eb[i] is '1':
            c = c * x % n
        print i, eb[i], c
    print '%d = %d^%d %% %d' % ( c, x, e, n)
    return c        

def FastEllipticCurve( k, P, N, a, b ):
    """ calculate kP mod N, where P is tuple (x,y) """
            
    kb = int2bin( k )
    beta = len( kb )

    P1 = P
    P2 = P
    P3 = [0,0] # just for Python init
    
    print kb, len( kb )
    
    for i in range( beta ):
    # for i in range( beta - 2, -1, -1):
        P3[0], P3[1] = 2 * P1[0] % N, 2 * P1[1] % N
        if kb[i] is '1':
            l = find_lam( P1[0], P1[1], P2[0], P2[1], a, N)
            P3[0] += update_x( l, P1[0], P2[0], N)
            P3[1] += update_y( l, P1[0], P3[0], P1[1], N)
            
        print '%d (%d, %d)' % (i, P3[0], P3[1])

        P2[0], P2[1] = P3[0], P3[1]

def Alg_221( q, j ):
    """ Base-q Fermat Pseudo-primality test """
    
    for i in range( 3, j, 1 ):
        
        if ( (q ** i) % i ) == 2:
        
            print '%8d is a base %d pseudo-prime' % ( i, q )
            
    
if __name__ == '__main__':
    # print Alg_121( 41 )
    # gcd = Alg_Euclid
    # gcd = Alg_improved_Euclid
    # print gcd( 25, 50 )
    # print gcd( 1281, 243 )
    # print gcd( 1403, 549 )
    # print Alg_122( 7 )
    
    # find_order( 11, 31 )
    # exercise_172( 3, 2, -2, -3, 7, 10)
    #exercise_172( 0, 1, -1, -1, 1094813, 8)
    # 
    # FastModExp_01( 7, 9007, 561)
    # 
    #FastEllipticCurve( 8, [0,1], 1098413, -1, -1 )
    
    Alg_221( 2, 1000 )
    
    
    
    