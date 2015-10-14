'''
Created on Dec 14, 2011

@author: pablocelayes
'''

#!/usr/bin/python
# -*- coding: utf-8 -*-
"""\

This module generates RSA-keys which are vulnerable to
the Wiener continued fraction attack

(see RSAfracCont.pdf)

The RSA keys are obtained as follows:
1. Choose two prime numbers p and q
2. Compute n=pq
3. Compute phi(n)=(p-1)(q-1)
4. Choose e coprime to phi(n) such that gcd(e,n)=1
5. Compute d = e^(-1) mod (phi(n))
6. e is the publickey; n is also made public (determines the block size); d is the privatekey

Encryption is as follows:
1. Size of data to be encrypted must be less than n
2. ciphertext=pow(plaintext,publickey,n)

Decryption is as follows:
1. Size of data to be decrypted must be less than n
2. plaintext=pow(ciphertext,privatekey,n)

-------------------------------

RSA-keys are Wiener-vulnerable if d < (n^(1/4))/sqrt(6)

"""

import random, MillerRabin, Arithmetic

def getPrimePair(bits=512):
    '''
    genera un par de primos p , q con 
        p de nbits y
        p < q < 2p
    '''
    
    assert bits%4==0
    
    p = MillerRabin.gen_prime(bits)
    q = MillerRabin.gen_prime_range(p+1, 2*p)
    
    return p,q

def generateKeys(nbits=1024):
    '''
    Generates a key pair
        public = (e,n)
        private = d 
    such that
        n is nbits long
        (e,n) is vulnerable to the Wiener Continued Fraction Attack
    '''
    # nbits >= 1024 is recommended
    assert nbits%4==0
    
    p,q = getPrimePair(nbits//2)
    n = p*q
    phi = Arithmetic.totient(p, q)
        
    # generate a d such that:
    #     (d,n) = 1
    #    36d^4 < n
    good_d = False
    while not good_d:
        d = random.getrandbits(nbits//4)
        if (Arithmetic.gcd(d,phi) == 1 and 36*pow(d,4) < n):
            good_d = True
                    
    e = Arithmetic.modInverse(d,phi)
    return e,n,d

if __name__ == "__main__":
    print("hey")
    for i in range(5):
        e,n,d = generateKeys()
        print ("Clave Publica:")
        print("e =")
        print(e)
        print("n =")
        print(n)
        print ("Clave Privada:")
        print("d =")
        print(d)
        print("-----------------------")
