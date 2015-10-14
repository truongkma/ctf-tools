/*
 * Implementation for "Reconstructing RSA Private Keys from Random Key
 * Bits," in proc. Crypto 2009, vol. 5677 of LNCS, pp. 1--17.
 * Springer-Verlag, Aug. 2009.
 *
 * Written by Nadia Heninger and Hovav Shacham.
 *
 * Copyright (c) 2009, The Regents of the University of California.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * 3. Neither the name of the University nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

// C:
#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <limits.h>
#include <sys/time.h>
// *shudder* STL:
#include <iostream>
#include <fstream>
#include <iomanip>
#include <queue>
// NTL:
#include <NTL/ZZ.h>
#include <NTL/LLL.h>
#include <NTL/mat_ZZ.h>
#include <NTL/vec_ZZ.h>
#include <NTL/ZZ_p.h>
#include <NTL/ZZ_pX.h>
#include <NTL/vec_ZZ_p.h>
#include <NTL/ZZ_pXFactoring.h>
#include <NTL/LLL.h>

NTL_CLIENT


void
ClrBit(ZZ& x, long p)
{
  if (bit(x,p))
    SwitchBit(x,p);
}

void
sbit(ZZ& x, long p, int val)
{
  if (bit(x,p) != val)
    SwitchBit(x,p);
}

struct rsa_pub {
  // public:
  ZZ N;
  ZZ e;
};

struct rsa_priv {
  // private:
  ZZ p;
  ZZ q;
  ZZ d;
  // additional private:
  ZZ dp1;
  ZZ dq1;
};

void
make_rsa_key(rsa_pub &pub, rsa_priv &priv, long bits, ZZ& e)
{
  pub.e = e;

  do
    {
      GenPrime(priv.p, bits/2);
    }
  while (!IsOne(GCD(priv.p-1, pub.e)));

  do
    {
      GenPrime(priv.q, bits/2);
    }
  while (!IsOne(GCD(priv.q-1, pub.e)));

  pub.N = priv.p * priv.q;

  priv.d = InvMod(pub.e, (priv.p-1)*(priv.q-1));

  rem(priv.dp1, priv.d, priv.p-1);
  rem(priv.dq1, priv.d, priv.q-1);
}

void
write_rsa_key(char *filename,
              rsa_pub &pub, rsa_priv &priv, long bits)
{
  ofstream file(filename);
  if (!file)
    {
      cerr << "Error: can't open output file " << filename << endl;
      exit(1);
    }
  
  file << bits << endl;
  file << pub.N << endl;
  file << pub.e << endl;
  file << priv.p << endl;
  file << priv.q << endl;
  file << priv.d << endl;
  file << priv.dp1 << endl;
  file << priv.dq1 << endl;
}

void
read_rsa_key(char *filename,
              rsa_pub &pub, rsa_priv &priv, int &bits)
{
  ifstream file(filename);
  if (!file)
    {
      cerr << "Error: can't open output file " << filename << endl;
      exit(1);
    }
  
  file >> bits;
  file >> pub.N;
  file >> pub.e;
  file >> priv.p;
  file >> priv.q;
  file >> priv.d;
  file >> priv.dp1;
  file >> priv.dq1;
}

// Prints info about the program's command line options
static void
usage(void)
{
    fprintf(stderr,
            "Usage: keygen [OPTIONS]\n"
            "\n"
            "\t-e E\tsets e to E (default is 65537)\n"
            "\t-n N\tsets size of modulus to N bits (default is 2048)\n"
            "\t-o FILE\twrites to file FILE (default is stdout)\n"
            "\t-s\tomits seeding the PRNG from /dev/urandom\n"
            "\t-h\tprint this message\n");
}

#define RANDBYTES 16

static void
seed(void)
{
  int fd;
  unsigned char randbuf[RANDBYTES];

  if ( (fd = open("/dev/urandom", O_RDONLY, 0)) < 0)
    {
      cerr << "Error: Can't open /dev/urandom." << endl;
      exit(1);
    }
  if (read(fd, randbuf, RANDBYTES) != RANDBYTES)
    {
      cerr << "Error: Can't read from /dev/urandom." << endl;
      exit(1);
    }
  if (close(fd) < 0)
    {
      cerr << "Error: Can't close /dev/urandom." << endl;
      exit(1);
    }
  SetSeed(ZZFromBytes(randbuf, RANDBYTES));
}

int
main(int argc, char *argv[])
{
  rsa_pub pub;
  rsa_priv key;

  int do_seed = 1;
  int MODULUS_BITS = 2048;
  ZZ E; E = 65537;

  char *filein = NULL;
  char *filename = "/dev/fd/1"; // stdout

  int c;
  while((c = getopt(argc, argv, "e:n:so:i:h")) != EOF)
    switch (c)
      {
      case 'e':
        E = atoi(optarg);
        break;
      case 'n':
        MODULUS_BITS = atoi(optarg);
        break;
      case 's':
        do_seed = 0;
        break;
      case 'i':
        filein = optarg;
        break;
      case 'o':
        filename = optarg;
        break;
      case 'h':
        usage();
        exit(0);
      }

  if (do_seed)
    seed();

  if (filein)
    read_rsa_key(filein, pub, key, MODULUS_BITS);
  else
    make_rsa_key(pub, key, MODULUS_BITS, E);

  write_rsa_key(filename, pub, key, MODULUS_BITS);

  return 0;
}
