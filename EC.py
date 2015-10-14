__author__ = 'kma'
# Basics of Elliptic Curve Cryptography implementation on Python
import collections


def inv(n, q):
    for i in range(q):
        if (n * i) % q == 1:
            return i
        pass
    assert False, "unreached"
    pass


def sqrt(n, q):

    assert n < q
    for i in range(1, q):
        if i * i % q == n:
            return (i, q - i)
        pass

Coord = collections.namedtuple("Coord", ["x", "y"])

class EC(object):
    """System of Elliptic Curve"""
    def __init__(self, a, b, q):
        assert 0 < a and a < q and 0 < b and b < q and q > 2
        assert (4 * (a ** 3) + 27 * (b ** 2))  % q != 0
        self.a = a
        self.b = b
        self.q = q
        self.zero = Coord(0, 0)
        pass

    def is_valid(self, p):
        if p == self.zero: return True
        l = (p.y ** 2) % self.q
        r = ((p.x ** 3) + self.a * p.x + self.b) % self.q
        return l == r

    def at(self, x):
        assert x < self.q
        ysq = (x ** 3 + self.a * x + self.b) % self.q
        y, my = sqrt(ysq, self.q)
        return Coord(x, y), Coord(x, my)

    def neg(self, p):
        return Coord(p.x, -p.y % self.q)

    def add(self, p1, p2):
        """<add> of elliptic curve: negate of 3rd cross point of (p1,p2) line
        """
        if p1 == self.zero: return p2
        if p2 == self.zero: return p1
        if p1.x == p2.x and (p1.y != p2.y or p1.y == 0):
            # p1 + -p1 == 0
            return self.zero
        if p1.x == p2.x:
            # p1 + p1: use tangent line of p1 as (p1,p1) line
            l = (3 * p1.x * p1.x + self.a) * inv(2 * p1.y, self.q) % self.q
            pass
        else:
            l = (p2.y - p1.y) * inv(p2.x - p1.x, self.q) % self.q
            pass
        x = (l * l - p1.x - p2.x) % self.q
        y = (l * (p1.x - x) - p1.y) % self.q
        return Coord(x, y)

    def mul(self, p, n):
        r = self.zero
        m2 = p
        # O(log2(n)) add
        while 0 < n:
            if n & 1 == 1:
                r = self.add(r, m2)
                pass
            n, m2 = n >> 1, self.add(m2, m2)
            pass
        # [ref] O(n) add
        #for i in range(n):
        #    r = self.add(r, p)
        #    pass
        return r

    def order(self, g):
        assert self.is_valid(g) and g != self.zero
        for i in range(1, self.q + 1):
            if self.mul(g, i) == self.zero:
                return i
            pass
    pass


if __name__=='__main__':
    print "Welcome to EC calculator"
    #input EC
    print "Please input p a b:"
    e = raw_input(">")
    e = e.split(" ")
    q = int(e[0])
    a = int(e[1])
    b = int(e[2])
    E = EC(a,b,q)
    #input P
    print "Please input P(x1,y1): "
    x1 = int(raw_input("x1="))
    y1 = int(raw_input("y1="))
    p1 = Coord(x1, y1)
    answer = raw_input("1: Add\n2: Multiplication\n")
    if (answer not in ['1','2']):
        answer = raw_input("1: Add\n2: Multiplication\n")
    if (answer=='1'):
        print "Please input Q(x2,y2)"
        x2 = int(raw_input("x2="))
        y2 = int(raw_input("y2="))
        p2 = Coord(x2, y2)
        kq = E.add(p1,p2)
        print "P + Q = ", kq
    if (answer == '2'):
        print "Please input k:"
        k = int(raw_input(">"))
        kq = E.mul(p1,k)
        print "%dP = " % k, kq

