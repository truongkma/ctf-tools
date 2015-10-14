import math
import random

############################
## Wiener's Attack module ##
############################

# Calculates bitlength


def bitlength(x):
    assert x >= 0
    n = 0
    while x > 0:
        n = n + 1
        x = x >> 1
    return n

# Squareroots an integer


def isqrt(n):
    if n < 0:
        raise ValueError('square root not defined for negative numbers')
    if n == 0:
        return 0
    a, b = divmod(bitlength(n), 2)
    x = 2**(a + b)
    while True:
        y = (x + n // x) // 2
        if y >= x:
            return x
        x = y

# Checks if an integer has a perfect square


def is_perfect_square(n):
    h = n & 0xF  # last hexadecimal "digit"
    if h > 9:
        return -1  # return immediately in 6 cases out of 16.
    # Take advantage of Boolean short-circuit evaluation
    if (h != 2 and h != 3 and h != 5 and h != 6 and h != 7 and h != 8):
        # take square root if you must
        t = isqrt(n)
        if t * t == n:
            return t
        else:
            return -1
    return -1

# Calculate a sequence of continued fractions


def partial_quotiens(x, y):
    partials = []
    while x != 1:
        partials.append(x // y)
        a = y
        b = x % y
        x = a
        y = b
    # print partials
    return partials

# Helper function for convergents


def indexed_convergent(sequence):
    i = len(sequence) - 1
    num = sequence[i]
    denom = 1
    while i > 0:
        i -= 1
        a = (sequence[i] * num) + denom
        b = num
        num = a
        denom = b
    #print (num, denom)
    return (num, denom)

# Calculate convergents of a  sequence of continued fractions


def convergents(sequence):
    c = []
    for i in range(1, len(sequence)):
        c.append(indexed_convergent(sequence[0:i]))
    # print c
    return c

# Calculate `phi(N)` from `e`, `d` and `k`


def phiN(e, d, k):
    return ((e * d) - 1) / k

# Wiener's attack, see http://en.wikipedia.org/wiki/Wiener%27s_attack for
# more information


def wiener_attack(N, e):
    (p, q, d) = (0, 0, 0)
    conv = convergents(partial_quotiens(e, N))
    for frac in conv:
        (k, d) = frac
        if k == 0:
            continue
        y = -(N - phiN(e, d, k) + 1)
        discr = y * y - 4 * N
        if(discr >= 0):
            # since we need an integer for our roots we need a perfect squared
            # discriminant
            sqr_discr = is_perfect_square(discr)
            # test if discr is positive and the roots are integers
            if sqr_discr != -1 and (-y + sqr_discr) % 2 == 0:
                p = ((-y + sqr_discr) / 2)
                q = ((-y - sqr_discr) / 2)
                return p, q, d
    return p, q, d
e = 0x0285F8D4FE29CE11605EDF221868937C1B70AE376E34D67F9BB78C29A2D79CA46A60EA02A70FDB40E805B5D854255968B2B1F043963DCD61714CE4FC5C70ECC4D756AD1685D661DB39D15A801D1C382ED97A048F0F85D909C811691D3FFE262EB70CCD1FA7DBA1AA79139F21C14B3DFE95340491CFF3A5A6AE9604329578DB9F5BCC192E16AA62F687A8038E60C01518F8CCAA0BEFE569DADAE8E49310A7A3C3BDDCF637FC82E5340BEF4105B533B6A531895650B2EFA337D94C7A76447767B5129A04BCF3CD95BB60F6BFD1A12658530124AD8C6FD71652B8E0EB482FCC475043B410DFC4FE5FBC6BDA08CA61244284A4AB5B311BC669DF0C753526A79C1A57
n = 0x02AEB637F6152AFD4FB3A2DD165AEC9D5B45E70D2B82E78A353F7A1751859D196F56CB6D11700195F1069A73D9E5710950B814229AB4C5549383C2C87E0CD97F904748A1302400DC76B42591DA17DABAF946AAAF1640F1327AF16BE45B8830603947A9C3309CA4D6CC9F1A2BCFDACF285FBC2F730E515AE1D93591CCD98F5C4674EC4A5859264700F700A4F4DCF7C3C35BBC579F6EBF80DA33C6C11F68655092BBE670D5225B8E571D596FE426DB59A6A05AAF77B3917448B2CFBCB3BD647B46772B13133FC68FFABCB3752372B949A3704B8596DF4A44F085393EE2BF80F8F393719ED94AB348852F6A5E0C493EFA32DA5BF601063A033BEAF73BA47D8205DB
p, q, d = wiener_attack(n, e)
print p
print q
print d
################################
## End Wiener's Attack module ##
################################
