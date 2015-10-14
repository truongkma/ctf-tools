import fractions  # for gcd function (or easily implementable to avoid import)
import random  # for random elements drawing in RecoverPrimeFactors


def failFunction():
    print("Prime factors not found")


def outputPrimes(a, n):
    p = fractions.gcd(a, n)
    q = int(n / p)
    if p > q:
        p, q = q, p
    print("Found factors p and q")
    print("p = {0}".format(str(p)))
    print("q = {0}".format(str(q)))
    return p, q


def RecoverPrimeFactors(n, e, d):
    """The following algorithm recovers the prime factor
            s of a modulus, given the public and private
            exponents.
            Function call: RecoverPrimeFactors(n, e, d)
            Input: 	n: modulus
                            e: public exponent
                            d: private exponent
            Output: (p, q): prime factors of modulus"""

    k = d * e - 1
    if k % 2 == 1:
        failFunction()
        return 0, 0
    else:
        t = 0
        r = k
        while(r % 2 == 0):
            r = int(r / 2)
            t += 1
        for i in range(1, 101):
            g = random.randint(0, n)  # random g in [0, n-1]
            y = pow(g, r, n)
            if y == 1 or y == n - 1:
                continue
            else:
                for j in range(1, t):  # j \in [1, t-1]
                    x = pow(y, 2, n)
                    if x == 1:
                        p, q = outputPrimes(y - 1, n)
                        return p, q
                    elif x == n - 1:
                        continue
                    y = x
                    x = pow(y, 2, n)
                    if x == 1:
                        p, q = outputPrimes(y - 1, n)
                        return p, q
