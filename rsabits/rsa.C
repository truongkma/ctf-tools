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


static double
timenow(void)
{
  struct timeval thetime;

  gettimeofday(&thetime, NULL);
  return thetime.tv_sec + thetime.tv_usec / 1000000.0;
}

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

// masks for known bits in priv components:
struct rsa_mask {
  ZZ p;
  ZZ q;
  ZZ d;
  ZZ dp1;
  ZZ dq1;
};

struct rsa_ext {
  ZZ k;
  ZZ g;                         // aka x aka k_p
  ZZ h;                         // aka y aka k_q

  // powers of 2 in k,g,h:
  int k_bits;
  int g_bits;
  int h_bits;

  // constraint 4 rhs: k(N+1) + 1
  ZZ c4rhs;
};

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
degrade_rsa_key(rsa_mask &mask, rsa_priv &key, double delta)
{
  ZZ *masks[5];
  int lens[5];

  clear(mask.p);
  clear(mask.q);
  clear(mask.d);
  clear(mask.dp1);
  clear(mask.dq1);

  masks[0] = &(mask.p);   lens[0] = NumBits(key.p);
  masks[1] = &(mask.q);   lens[1] = NumBits(key.q);
  masks[2] = &(mask.d);   lens[2] = NumBits(key.d);
  masks[3] = &(mask.dp1); lens[3] = NumBits(key.dp1);
  masks[4] = &(mask.dq1); lens[4] = NumBits(key.dq1);

  int i;
  int totallen = 0;
  for (i = 0; i < 5; i++)
    totallen += lens[i];

  int NUM_KNOWN = delta*totallen;

  int r;
  int known = 0;
  while (known < NUM_KNOWN)
    {
      r = RandomBnd(totallen);
      
      for(i = 0; i < 5; i++)
        {
          if (r < lens[i])
            break;
          r -= lens[i];
        }

      if (bit(*(masks[i]), r) == 0)
        {
          SetBit((*masks[i]), r);
          known++;
        }
    }
}

// check bits i, start <= i < end;
long
degraded_match(ZZ &a, ZZ &a_mask, ZZ &b, long start, long end)
{
  for (long i = start; i < end; i++)
      if (bit(a_mask, i) == 1
          && bit(a,i) != bit(b,i))
        return 0;
  return 1;
}

// skip a few bits in the dk comparison.  shouldn't hurt.
#define FUZZ_BITS 80

long
find_k(ZZ &k, rsa_pub &pub, rsa_priv &key, rsa_mask &mask)
{
  ZZ dk;
  long nbits = NumBits(pub.N);

  for (k = 1; k < pub.e; k++)
    {
      dk = (k*pub.N + 1)/pub.e;
      if (degraded_match(key.d, mask.d, dk,
                         nbits/2+FUZZ_BITS, nbits))
        {
          return 1;
        }
    }
  return 0;
}

long
correct_d(ZZ &k, rsa_pub &pub, rsa_mask &mask)
{
  long start, i;
  ZZ dmin,dmax;

  dmax = (k*pub.N + 1)/pub.e;
  dmin = dmax - 3*SqrRoot(pub.N);
  
  // conservatively, copy only those bits that we're 100% sure about.
  for (start = NumBits(pub.N)-1;
       bit(dmax,start) == bit(dmin,start);
       start--)
    ;
  start++;                      // don't copy the disagreed-on bit

  for(i = start; i < NumBits(dmax); i++)
    SetBit(mask.d, i);          // all these bits are now known.

  return start;
}

void
ext_powers(rsa_ext &ext)
{
  ext.k_bits = NumTwos(ext.k);
  ext.g_bits = NumTwos(ext.g);
  ext.h_bits = NumTwos(ext.h);
}

void
find_gh(ZZ &g, ZZ &h, ZZ &k, rsa_pub &pub)
{
  ZZ_p::init(pub.e);

  ZZ_pX f;
  SetCoeff(f,2,to_ZZ_p(1));
  SetCoeff(f,1,to_ZZ_p(-(k*(pub.N-1)+1)));
  SetCoeff(f,0,to_ZZ_p(-k));

  vec_ZZ_p list_of_roots;
  FindRoots(list_of_roots,f);

  g = rep(list_of_roots[0]);
  h = rep(list_of_roots[1]);
}

// x <- e^{-1} mod 2^{bits}
void
set_pow2_inverse(ZZ &x, ZZ &e, long bits)
{
  ZZ modulus = power2_ZZ(bits);
  InvMod(x, e % modulus, modulus);
}

// initialize the search key.  we know the 0th bit for all entries
// and a few more bits for d, d_p, and d_q:
void
set_start_key(rsa_pub &pub, rsa_ext &ext, rsa_priv &priv)
{
  // p and q are both odd, so set their 0th bit:
  priv.p = 1;
  priv.q = 1;

  // ed = rhs = 1 mod 2^{k_bits + 1}
  set_pow2_inverse(priv.d, pub.e, ext.k_bits+1);
  // similarly for d_p and d_q
  set_pow2_inverse(priv.dp1, pub.e, ext.g_bits+1);
  set_pow2_inverse(priv.dq1, pub.e, ext.h_bits+1);
}


struct item {
  rsa_priv key;
  int i;
};

// entries: {p,q,d,dp,dq}
char possibilities[][5] = 
  {
    {0, 0, 0, 0, 0},
    {0, 0, 0, 0, 1},
    {0, 0, 0, 1, 0},
    {0, 0, 0, 1, 1},
    {0, 0, 1, 0, 0},
    {0, 0, 1, 0, 1},
    {0, 0, 1, 1, 0},
    {0, 0, 1, 1, 1},
    {0, 1, 0, 0, 0},
    {0, 1, 0, 0, 1},
    {0, 1, 0, 1, 0},
    {0, 1, 0, 1, 1},
    {0, 1, 1, 0, 0},
    {0, 1, 1, 0, 1},
    {0, 1, 1, 1, 0},
    {0, 1, 1, 1, 1},
    {1, 0, 0, 0, 0},
    {1, 0, 0, 0, 1},
    {1, 0, 0, 1, 0},
    {1, 0, 0, 1, 1},
    {1, 0, 1, 0, 0},
    {1, 0, 1, 0, 1},
    {1, 0, 1, 1, 0},
    {1, 0, 1, 1, 1},
    {1, 1, 0, 0, 0},
    {1, 1, 0, 0, 1},
    {1, 1, 0, 1, 0},
    {1, 1, 0, 1, 1},
    {1, 1, 1, 0, 0},
    {1, 1, 1, 0, 1},
    {1, 1, 1, 1, 0},
    {1, 1, 1, 1, 1}
  };

#define NUM_POSS 32

static int MODULUS_BITS = 2048;
static int VERBOSE = 0;
static int TIMING = 0;
static int PANICWIDTH = -1;
static ZZ E;

// statistics:
static int total_pushes = 0;
static int widest_seen = -1;

#define POSS_P  0
#define POSS_Q  1
#define POSS_D  2
#define POSS_DP 3
#define POSS_DQ 4

void
process_key(rsa_pub &pub, rsa_priv &realpriv, rsa_mask mask,
            rsa_ext &ext, queue<item> &Q, item &it)
{
  int j;
  char is_poss[NUM_POSS];
  memset(is_poss, 1, NUM_POSS);

  int i = it.i;

  /*
   * Constraints from known key bits
   */

  if (bit(mask.p,i) == 1)       // p bit known
    for (j = 0; j < NUM_POSS; j++)
      if (possibilities[j][POSS_P] != bit(realpriv.p,i))
        is_poss[j] = 0;

  if (bit(mask.q,i) == 1)       // q bit known
    for (j = 0; j < NUM_POSS; j++)
      if (possibilities[j][POSS_Q] != bit(realpriv.q,i))
        is_poss[j] = 0;

  if (bit(mask.d, i + ext.k_bits) == 1) // d bit known
    for (j = 0; j < NUM_POSS; j++)
      if (possibilities[j][POSS_D]
          != bit(realpriv.d, i + ext.k_bits))
        is_poss[j] = 0;

  if (bit(mask.dp1, i + ext.g_bits) == 1) // dp1 bit known
    for (j = 0; j < NUM_POSS; j++)
      if (possibilities[j][POSS_DP]
          != bit(realpriv.dp1, i + ext.g_bits))
        is_poss[j] = 0;

  if (bit(mask.dq1, i + ext.h_bits) == 1) // dq1 bit known
    for (j = 0; j < NUM_POSS; j++)
      if (possibilities[j][POSS_DQ]
          != bit(realpriv.dq1, i + ext.h_bits))
        is_poss[j] = 0;

  /*
   * Constraints from relations
   */

  // N = pq.
  if (bit(pub.N,i) == bit(it.key.p*it.key.q,i))
    {
      // p at i must agree with q at i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_P] != possibilities[j][POSS_Q])
          is_poss[j] = 0;
    }
  else
    {
      // p at i must *not* agree with q at i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_P] == possibilities[j][POSS_Q])
          is_poss[j] = 0;
    }

  // e d_p = g(p-1) + 1
  // CHEAT ALERT: +1 omitted on rhs because it can't change anything ...
  // CHEAT ALERT: instead of computing (p-1), clear p lsb, use p ...
  ClrBit(it.key.p,0);
  if (bit(pub.e*it.key.dp1, i + ext.g_bits) 
      == bit(ext.g*it.key.p, i + ext.g_bits))
    {
      // dp1 and p must agree at bit i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_DP] != possibilities[j][POSS_P])
          is_poss[j] = 0;
    }
  else
    {
      // dp1 and p must *dis*agree at bit i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_DP] == possibilities[j][POSS_P])
          is_poss[j] = 0;
    }
  SetBit(it.key.p,0);

  // e d_q = h(q-1) + 1
  // CHEAT ALERT: +1 omitted on rhs because it can't change anything ...
  // CHEAT ALERT: instead of computing (q-1), clear q lsb, use q ...
  ClrBit(it.key.q,0);
  if (bit(pub.e*it.key.dq1, i + ext.h_bits)
      == bit(ext.h*it.key.q, i + ext.h_bits))
    {
      // dp1 and q must agree at bit i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_DQ] != possibilities[j][POSS_Q])
          is_poss[j] = 0;
    }
  else
    {
      // dq1 and q must *dis*agree at bit i
      for (j = 0; j < NUM_POSS; j++)
        if (possibilities[j][POSS_DQ] == possibilities[j][POSS_Q])
          is_poss[j] = 0;
    }
  SetBit(it.key.q,0);

  // ed + k(p+q) = k(N-1) +1
  if (bit(pub.e*it.key.d + ext.k*(it.key.p+it.key.q), i + ext.k_bits)
      == bit(ext.c4rhs, i + ext.k_bits))
    {
      // sum of ith bits of d, p, and q must have parity 0
      for (j = 0; j < NUM_POSS; j++)
        if (1 == ((possibilities[j][POSS_D]
                   + possibilities[j][POSS_P]
                   + possibilities[j][POSS_Q]) & 0x1))
          is_poss[j] = 0;
    }
  else
    {
      // sum of ith bits of k, p, and q must have parity 1
      for (j = 0; j < NUM_POSS; j++)
        if (0 == ((possibilities[j][POSS_D]
                   + possibilities[j][POSS_P]
                   + possibilities[j][POSS_Q]) & 0x1))
          is_poss[j] = 0;
    }

  it.i = i+1;
  for (j = 0; j < NUM_POSS; j++)
    if (is_poss[j])
      {
        sbit(it.key.p,   i,
             possibilities[j][POSS_P]);
        sbit(it.key.q,   i,
             possibilities[j][POSS_Q]);
        sbit(it.key.d,   i + ext.k_bits,
             possibilities[j][POSS_D]);
        sbit(it.key.dp1, i + ext.g_bits,
             possibilities[j][POSS_DP]);
        sbit(it.key.dq1, i + ext.h_bits,
             possibilities[j][POSS_DQ]);

        Q.push(it); total_pushes++;
      }
}


// Prints info about the program's command line options
static void
usage(void)
{
    fprintf(stderr,
            "Usage: rsa [OPTIONS]\n"
            "\n"
            "\t-e E\tsets e to E (default is 65537)\n"
            "\t-n N\tsets number of bits in p to N (default is 1024)\n"
            "\t-f F\tsets fraction of known bits to F (default is .27)\n"
            "\t-s\tomits seeding the PRNG from /dev/urandom\n"
            "\t-v\tgives verbose output\n"
            "\t-t\tgives timing information\n"
            "\t-w W\tsets panic width to W (default is -1, meaning no limit)\n"
            "\t-i FILE\treads RSA key from FILE\n"
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
  rsa_mask mask;

  double delta = 0.27;

  int do_seed = 1;
  E = 65537;

  char *filename = NULL;

  int c;
  while((c = getopt(argc, argv, "e:n:f:svtw:i:h")) != EOF)
    switch (c)
      {
      case 'e':
        E = atoi(optarg);
        break;
      case 'n':
        MODULUS_BITS = atoi(optarg);
        break;
      case 'f':
        delta = atof(optarg);
        break;
      case 's':
        do_seed = 0;
        break;
      case 'v':
        VERBOSE = 1;
        break;
      case 't':
        TIMING = 1;
        break;
      case 'w':
        PANICWIDTH = atoi(optarg);
        break;
      case 'i':
        filename = optarg;
        break;
      case 'h':
        usage();
        exit(0);
      }

  if (do_seed)
    seed();

  if (filename)
    read_rsa_key(filename, pub, key, MODULUS_BITS);
  else
    make_rsa_key(pub, key, MODULUS_BITS, E);
  degrade_rsa_key(mask, key, delta);


  double start_time = 0.0, mid_time = 0.0, stop_time = 0.0;

  if (TIMING)
    start_time = timenow();

  ZZ k;

  if (!find_k(k, pub, key, mask))
    {
      cerr << "Error: k not found." << endl;
      return 1;
    }

  correct_d(k, pub, mask);

  ZZ g,h;

  find_gh(g, h, k, pub);

  rsa_ext ext_gh, ext_hg;

  // try g and h both ways
  ext_gh.g = g; ext_gh.h = h;
  ext_hg.g = h; ext_hg.h = g;

  ext_gh.k = ext_hg.k = k;

  // calculate powers of 2
  ext_powers(ext_gh);
  ext_powers(ext_hg);

  // precompute constraint 4 rhs: k(N+1) + 1
  ext_gh.c4rhs = ext_hg.c4rhs = k*(pub.N+1)+1;

  item start_gh, start_hg;

  start_gh.i = 1;
  set_start_key(pub, ext_gh, start_gh.key);

  start_hg.i = 1;
  set_start_key(pub, ext_hg, start_hg.key);

  queue<item> Q_gh, Q_hg;
  Q_gh.push(start_gh); total_pushes++;
  Q_hg.push(start_hg); total_pushes++;

  if (TIMING)
    mid_time = timenow();

#define STATE_BOTH_GH 0
#define STATE_BOTH_HG 1
#define STATE_GH_ONLY 2
#define STATE_HG_ONLY 3
#define STATE_NEITHER 4

  // for e=3, no point in running the same thing twice
  int state = (g == h)? STATE_GH_ONLY : STATE_BOTH_GH;
  int curi = 0;

  while (curi < MODULUS_BITS/2)
    switch (state)
      {
      case STATE_BOTH_GH:
        if (Q_gh.empty())
          {
            state = STATE_HG_ONLY;
          }
        else
          {
            item &it = Q_gh.front();

            if (it.i > curi)
              {
                state = STATE_BOTH_HG;
              }
            else
              {
                process_key(pub, key, mask,
                            ext_gh, Q_gh, it);
                Q_gh.pop();
              }
          }
        break;

      case STATE_BOTH_HG:
        if (Q_hg.empty())
          {
            state = STATE_GH_ONLY;
          }
        else
          {
            item &it = Q_hg.front();

            if (it.i > curi)
              {
                curi = it.i;

                int width = (int)(Q_gh.size()+Q_hg.size());
                if (widest_seen < width)
                  widest_seen = width;
                if (PANICWIDTH > 0 && PANICWIDTH < width)
                  {
                    cerr << "Error: Panic width exceeded at " << curi << "." << endl;
                    return 1;
                  }
                if (VERBOSE)
                  cout << setw(4) << curi << ":"
                       << setw(12) << Q_gh.size()
                       << setw(12) << Q_hg.size() << endl;
                state = STATE_BOTH_GH;
              }
            else
              {
                process_key(pub, key, mask,
                            ext_hg, Q_hg, it);
                Q_hg.pop();
              }
          }
        break;

      case STATE_GH_ONLY:
        if (Q_gh.empty())
          {
            state = STATE_NEITHER;
          }
        else
          {
            item &it = Q_gh.front();

            if (it.i > curi)
              {
                curi = it.i;

                int width = (int)Q_gh.size();
                if (widest_seen < width)
                  widest_seen = width;
                if (PANICWIDTH > 0 && PANICWIDTH < width)
                  {
                    cerr << "Error: Panic width exceeded at " << curi << "." << endl;
                    return 1;
                  }
                if (VERBOSE)
                  cout << setw(4) << curi << ":"
                       << setw(12) << Q_gh.size()
                       << setw(12) << "." << endl;
              }

            process_key(pub, key, mask,
                        ext_gh, Q_gh, it);
            Q_gh.pop();
          }
        break;

      case STATE_HG_ONLY:
        if (Q_hg.empty())
          {
            state = STATE_NEITHER;
          }
        else
          {
            item &it = Q_hg.front();

            if (it.i > curi)
              {
                curi = it.i;

                int width = (int)Q_hg.size();
                if (widest_seen < width)
                  widest_seen = width;
                if (PANICWIDTH > 0 && PANICWIDTH < width)
                  {
                    cerr << "Error: Panic width exceeded at " << curi << "." << endl;
                    return 1;
                  }
                if (VERBOSE)
                  cout << setw(4) << curi << ":"
                       << setw(12) << "."
                       << setw(12) << Q_hg.size() << endl;
              }

            process_key(pub, key, mask,
                        ext_hg, Q_hg, it);
            Q_hg.pop();
          }
        break;

      case STATE_NEITHER:
        cerr << "Error: queues empty." << endl;
        return 1;
      }

  if (TIMING)
    stop_time = timenow();

  int found = 0;
  while (!Q_gh.empty())
    {
      item &soln = Q_gh.front();
      if (soln.key.p == key.p)
        {
          found = 1;
          break;
        }
      Q_gh.pop();
    }

  while (!Q_hg.empty())
    {
      item &soln = Q_hg.front();
      if (soln.key.p == key.p)
        {
          found = 1;
          break;
        }
      Q_hg.pop();
    }

  if (!found)
    {
      cerr << "Finished!  Key not found." << endl;
      return 1;
    }

  if (VERBOSE)
    {
      cout << "Key found." << endl;
      if (TIMING)
        cout << "Time elapsed: "
             << setprecision(3) << fixed << (stop_time - start_time)
             << " sec" << endl;
      cout << "Keys examined:  " << total_pushes << endl;
      cout << "Max width seen: " << widest_seen << endl;
    }
  else
    {
      if (TIMING)
        cout << setprecision(6) << fixed
             << (mid_time - start_time) << "\t"
             << (stop_time - mid_time)  << "\t";

      cout << total_pushes << "\t" << widest_seen << endl;
    }


  return 0;
}
