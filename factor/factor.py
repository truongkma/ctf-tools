#!/usr/bin/env python
# encoding: utf-8
"""
chapter_2.py
Created by Daniel O'Donovan on 2008-10-09.
Copyright (c) 2008 University of Cambridge. All rights reserved.
"""

import sys
import os
import math
import gmpy

# Test case:
# the non-trivial factors of 27595893247589237508237458728307 are
# 5253107790730936 and 5253250903452230


def int2bin(n, count=24):
    """returns the binary of integer n, using count number of digits"""
    return "".join([str((n >> y) & 1) for y in range(count - 1, -1, -1)])


def alg_231(n, improved=True):
    """ Page 197: Trial Division """
    # [1]
    t = 0
    k = 2
    dk = 2
    sqrt_n = math.sqrt(n)
    count = 0
    while True:

        if count > sqrt_n:
            break
        if int(n) == 1:
            break    # [2]

        if improved:
            dk = int(gmpy.next_prime(dk))

        # [3]
        if improved:
            q = n / dk
            r = n % dk
        else:
            q = n / k
            r = n % k

        if r != 0:

            if improved:
                if q > dk:
                    k += 1
                else:
                    t += 1
                    pt = n
            else:
                if q > k:       # [4]
                    k += 1
                else:
                    t += 1
                    pt = n
        else:
            t += 1
            if improved:
                pt = dk
            else:
                pt = k
            n = q
            break

        count += 1
        # print( q, r )

    print(n, pt)


def FermatFactAlg(n):
    """ Fermat's factoring algorithm 2.5.3 p 196 """
    n = gmpy.mpz(n)
    if n % 2 == 0:
        print("%d is even" % n)
    # gmpy.sqrt is largest truncated sqrt
    # k = int( math.sqrt(n) ) + 1
    k = gmpy.sqrt(n) + 1
    y = k ** 2 - n
    d = 1

    while True:
        # floor_sqrt_y = float( int( math.sqrt(y) ) )
        floor_sqrt_y = gmpy.sqrt(y)
        if ((floor_sqrt_y ** 2) ** 2) == (y ** 2):
            break
        else:
            y = y + 2 * k + d
            d += 2

        # print floor_sqrt_y, gmpy.qdiv( n, 2.0)
        # print ((floor_sqrt_y ** 2) ** 2), (y ** 2)

        if floor_sqrt_y > gmpy.qdiv(n, 2):
            print("No factor found ")
            return

    x = gmpy.sqrt(n + y)
    y = gmpy.sqrt(y)

    print(" the non-trivial factors of %d are" % n)
    print(" %d and %d" % (x - y, x + y))


def PollardsRho(N):
    """ Pollard's Rho method for factoring """
    from exercises import Alg_improved_Euclid as gcd
    from random import randint

    N = gmpy.mpz(N)

    """ generator function """
    def f(x, N):
        return (((x ** 2) + 1) % N)

    t = 75 * gmpy.sqrt(N)
    sqrt_t = gmpy.sqrt(t)

    factor_found = False
    while not factor_found:
        xim1 = randint(1, gmpy.sqrt(N) / 10)  # seed
        yim1 = f(f(xim1, N), N)

        i = 0
        while i < sqrt_t:
            xi = f(xim1, N)
            yi = f(f(yim1, N), N)
            # yi =    f( yim1, N )
            # xi = f( f( xim1, N ), N )

            # print( 'gcd( xi - yi ) = gcd( %d )' % abs(xi - yi) )
            d = gcd(abs(xi - yi), N)
            if d != 1:
                print('Non trivial factor found: ', d)
                factor_found = True
                break
            if xi == yi % N:
                print('Running with new seed')
                break

            xim1 = xi
            yim1 = yi
            i += 1


def shanks(y, a, n):
    """ Shanks' baby-step giant-step for finding discrete logarithms 
        of form : x = log_a ( y mod n )
    """
    s = gmpy.sqrt(n)

    S = {}  # calculate the baby steps
    T = {}  # calculate the giant steps
    for i in range(s):
        S['%s' % gmpy.mpz((y * (a ** i)) % n)] = int(i)
        T['%s' % gmpy.mpz((a ** ((i + 1) * s)) % n)] = int(i)

    # mathching and computing
    for key in S.keys():
        if key in T:
            r = S[key]
            st = (T[key] + 1) * s
            break
    x = st - r

    print 'So        log_%d %d\t(mod %d) =\t%d ' % (a, y, n, x)
    print 'or equiv.     %d^%d\t(mod %d) =\t%d ' % (a, x, n, y)
    return x

if __name__ == '__main__':
    print FermatFactAlg(278153)
    # FermatFactAlg( 340282366920938463463374607431768211457L )
    # FermatFactAlg( 3248523672894567297 )

    # PollardsRho( 1387 )
    # print PollardsRho( 278153 )
    # PollardsRho( 3248523672894567297)
    p = 267336782497463360204553349940982883027638137556242083062698936408269688347005688891456763746542347101087588816598516438470521580823690287174602955234443428763823316700034360179480125173290116352018408224011457777828019316565914911469044306734393178495267664516045383245055214352730843748251826260401437050527
    q = 133668391248731680102276674970491441513819068778121041531349468204134844173502844445728381873271173550543794408299258219235260790411845143587301477617221714381911658350017180089740062586645058176009204112005728888914009658282957455734522153367196589247633832258022691622527607176365421874125913130200718525263
    g = 2
    r = 115555594366429713423294552616937675916118120504744961563641525013140040664142792583845984606508402458231853767550443706825977496261343032708387092287400126258100958459122576423639320901367286214729498690662819998517533646029553339413177903415697834594318763749014338449403090885862083324407445091149939021161
    print 'hai'
    print PollardsRho(r)
    print 'truong'
    #x = shanks( 67, 59, 113 )
    #xx = shanks( r, g, p )
    # print x
