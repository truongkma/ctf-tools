# factmsieve.py - A Python driver for GGNFS and MSIEVE
#
# Copyright (c) 2010, Brian Gladman
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with
# or without modification, are permitted provided that the
# following conditions are met:
#
#    Redistributions of source code must retain the above
#    copyright notice, this list of conditions and the
#    following disclaimer.
#
#    Redistributions in binary form must reproduce the
#    above copyright notice, this list of conditions and
#    the following disclaimer in the documentation and/or
#    other materials provided with the distribution.
#
#    The names of its contributors may not be used to
#    endorse or promote products derived from this
#    software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# This code is a conversion of the script factmsieve.pl
# which is Copyright 2004, Chris Monico. His contribution
# is acknowledged, as are those of all who contributed to
# the original Perl script.
#
# I also acknowledge the invaluable help I have had from
# Jeff Gilchrist in testing amd debugging this driver.
# Without his support during its development, it would
# never have reached a working state.
#
# The support of Wingware, who kindly donated their frst
# class Python development environment, is acknowledged.

from __future__ import print_function

import os, sys, random, re, functools, string, socket, signal
import time, subprocess, gzip, glob, math, tempfile, datetime
import atexit, threading, collections, multiprocessing, platform

# Set binary directory paths

GGNFS_PATH = '../../bin/x64/Release/'
MSIEVE_PATH = '../../../msieve/build.vc10/x64/Release/'

# Set the number of CPU cores and threads
NUM_CORES = 4
THREADS_PER_CORE = 1
# number of siever threads to launch
SV_THREADS = NUM_CORES * THREADS_PER_CORE
# number of linear algebra threads to launch
LA_THREADS = NUM_CORES * THREADS_PER_CORE

USE_CUDA = True
GPU_NUM = 0

# Set global flags to control operation

CHECK_BINARIES = True
CHECK_POLY = True
CLEANUP = False
DOCLASSICAL = False
NO_DEF_NM_PARAM = False
PROMPTS = False
SAVEPAIRS = True
USE_KLEINJUNG_FRANKE_PS = False
USE_MSIEVE_POLY = True
VERBOSE = True

# End of configuration options

# ggnfs and msieve executable flie names

MSIEVE = 'msieve'

MAKEFB = 'makefb'
PROCRELS = 'procrels'

POL51M0 = 'pol51m0b'
POL51OPT = 'pol51opt'
POLYSELECT = 'polyselect'

PLOT = 'autogplot.sh'

# default parameter files

DEFAULT_PAR_FILE = GGNFS_PATH + 'def-par.txt'
DEFAULT_POLSEL_PAR_FILE = GGNFS_PATH + 'def-nm-params.txt'

# temporary files

PARAMFILE = '.params'
RELSBIN = 'rels.bin'

if sys.platform.startswith('win'):
  EXE_SUFFIX = '.exe'
else:
  EXE_SUFFIX = ''
  NICE_PATH = ''
  MSIEVE = './' + MSIEVE

# static global variables

PNUM = 0
LARGEP = 3
LARGEPRIMES = '-' + str(LARGEP) + 'p'
nonPrefDegAdjust = 12
polySelTimeMultiplier = 1.0

# poly5 parameters

pol5_p = { 'max_pst_time':0, 'search_a5step':0, 'npr':0, 'normmax':0,
           'normmax1':0, 'normmax2':0, 'murphymax':0 }

# poly select parameters

pols_p = { 'degree':0, 'maxs1':0, 'maxskew':0, 'goodscore':0,
           'examinefrac':0, 'j0':0, 'j1':0, 'estepsize':0, 'maxtime':0 }

# lattice sieve parameters

lats_p = { 'rlim':0, 'alim':0, 'lpbr':0, 'lpba':0, 'mfbr':0, 'mfba':0,
           'rlambda':0, 'alambda':0, 'qintsize':0, 'lss':1,
           'siever': 'gnfs-lasieve4I10e', 'minrels':0, 'currels':0 }

# classical sieve parameters

clas_p = { 'a0':0, 'a1':0, 'b0':0, 'b1':0, 'cl_a':0, 'cl_b':0 }

# polynomial parameters

poly_p = { 'n':0, 'degree':0, 'm':0, 'skew':0.0, 'coeff':dict() }

# factorisation parameters

fact_p = { 'n':0, 'dec_digits':0, 'type':0, 'knowndiv':0, 'snfs_difficulty':0,
           'digs':0, 'qstart':0, 'qstep':0, 'q0':0, 'dd':0, 'primes':list(),
           'comps':list(), 'divisors':list(),
           'q_dq':collections.deque([(0,0,0)] * SV_THREADS) }

# Utillity Routines

# print an error message and exit

def die(x, rv = -1):
  print(x)
  sys.exit(rv)

def sig_exit(x, y):
  die('Signal caught. Terminating...')

# obtain a float or an int from a string

def get_nbr(s):
  m = re.match('[+-]?([0-9]*\.)?[0-9]+([eE][+-]?[0-9]+)?', s)
  return float(s) if m else int(s)

# delete a file (unlink equivalent)

def delete_file(fn):
  if os.path.exists(fn):
    try:
      os.unlink(fn)
    except WindowsError:
      pass

# GREP on a list of text lines

def grep_l(pat, lines):
  r = []
  for l in lines:
    if re.search(pat, l):
      r += [re.sub('\r|\n', ' ', l)]
  return r

# GREP on a named file

def grep_f(pat, file_path):
  if not os.path.exists(file_path):
    raise IOError
  else:
    r = []
    with open(file_path, 'r') as in_file:
      for l in in_file:
        if re.search(pat, l):
          r += [re.sub('\r|\n', ' ', l)]
    return r

# concatenate file 'app' to file 'to'

def cat_f(app, to):
  if os.path.exists(app):
    if VERBOSE:
      print('appending {0:s} to {1:s}'.format(app, to))
    with open(to, 'ab') as out_file:
      with open(app, 'rb') as in_file:
        buf = in_file.read(8192)
        while buf:
          out_file.write(buf)
          buf = in_file.read(8192)

# compress file 'fr' to file 'to'

def gzip_f(fr, to):
  if not os.path.exists(fr):
    raise IOError
  else:
    if VERBOSE:
      print('compressing {0:s} to {1:s}'.format(fr, to))
    with open(fr, 'rb') as in_file:
      out_file = gzip.open(to, 'ab')
      out_file.writelines(in_file)
      out_file.close()

# remove end of line characters from a line

def chomp(s):
  p  = len(s)
  while p and (s[p - 1] == '\r' or s[p - 1] == '\n'):
    p -= 1
  return s[0:p]

# remove comment lines

def chomp_comment(s):
  return re.sub('#.*', '', s)

# remove all white space in a line

def remove_ws(s):
  return re.sub('\s', '', s)

# produce date/time string for log

def date_time_string() :
  dt = datetime.datetime.today()
  return dt.strftime('%a %b %d %H:%M:%S %Y ')

# write string to log(s):

def write_string_to_log(s):
  with open(LOGNAME, 'a') as out_f:
    print(date_time_string() + s, file = out_f)

def output(s, console = True, log = True):
  if console:
    print(s)
  if log:
    write_string_to_log(s)

    # find processor speed
    
def proc_speed():
  if os.sys.platform.startswith('win'):
    if sys.version_info[0] == 2:
      from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE
    else:
      from winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE
    h = OpenKey(HKEY_LOCAL_MACHINE, 
              'HARDWARE\\DESCRIPTION\\System\\CentralProcessor\\0')      
    mhz = float(QueryValueEx(h, '~MHz')[0])
  else:
    tmp = grep_f('cpu MHz\s+:\s+', '/proc/cpuinfo')
    m = re.search('\s*cpu MHz\s+:\s+([0-9]+)', tmp[0])
    mhz = float(m.group(1)) if m else 0.0
  return 1e-3 * mhz

# check that an executable file exists

def check_binary(exe):
  if CHECK_BINARIES:
    pth = MSIEVE_PATH if exe == MSIEVE else GGNFS_PATH 
    if not os.path.exists(pth + exe + EXE_SUFFIX):
      print('-> Could not find the program: {0:s}.'.format(exe))
      print('-> Did you set the paths properly in this script?')
      print('-> They are currently set to:')
      print('-> GGNFS_BIN_PATH = {0:s}'.format(GGNFS_PATH))
      print('-> MSIEVE_BIN_PATH = {0:s}'.format(MSIEVE_PATH))
      sys.exit(-1)

# run an executable file

def run_exe(exe, args, inp = '', in_file = None, out_file = None,
                log = True, display = VERBOSE, wait = True):
  al = {} if VERBOSE else {'creationflags' : 0x08000000 }
  if sys.platform.startswith('win'):
#   priority_high = 0x00000080
#   priority_normal = 0x00000020
#   priority_idle = 0x00000040
    al['creationflags'] = al.get('creationflags', 0) | 0x00000040
  else:
    al['preexec_fn'] = NICE_PATH

  if in_file and os.path.exists(in_file):
    al['stdin'] = open(in_file, 'r')

  if out_file:
    if out_file == subprocess.PIPE:
      md = '> PIPE'
      al['stdout'] = subprocess.PIPE
    elif os.path.exists(out_file):
      md = '>> ' + out_file
      al['stdout'] = open(out_file, 'a')
    else:
      md = '> ' + out_file
      al['stdout'] = open(out_file, 'w')

  cs = '-> {0:s} {1:s}'.format(exe, args)
  if in_file:
    cs += '< {0:s}'.format(in_file)
  if out_file:
    cs += md

  output(cs, console = display, log = log)

  ex = ((GGNFS_PATH if exe != MSIEVE
         else '') + exe + EXE_SUFFIX)

  p = subprocess.Popen([ex] + args.split(' '), **al)

  if not wait:
    return p

  if out_file == subprocess.PIPE:
    if sys.version_info[0] == 3:
      res = p.communicate(inp.encode())[0].decode()
    else:
      res = p.communicate(inp)[0]
    if res:
      res = re.split('(?:\r|\n)*', res)
    ret = p.poll()
    return (ret, res)
  else:
    return p.wait()

def run_msieve(ap):
  cwd = os.getcwd()
  msd = os.path.abspath(os.path.join(cwd, MSIEVE_PATH))
  os.chdir(msd)
  rel = os.path.relpath(cwd)
  dp = os.path.join(rel, DATNAME)
  lp = os.path.join(rel, LOGNAME)
  ip = os.path.join(rel, ININAME)
  fp = os.path.join(rel, FBNAME)
  args = ('-s {0:s} -l {1:s} -i {2:s} -nf {3:s} '
          .format(dp, lp, ip, fp))
  ret = run_exe(MSIEVE, args + ap)
  os.chdir(cwd)
  return ret

# generate a list of primes

def prime_list(n):
  sieve = [False, False] + [True] * (n - 1)
  for i in range(2, int(n ** 0.5) + 1):
    if sieve[i]:
      m = n // i - i
      sieve[i * i : n + 1 : i] = [False] * (m + 1)
  return [i for i in range(n + 1) if sieve[i]]

# greatest common divisor

def gcd(x, y):
  if x == 0:
    return y
  elif y == 0:
    return x
  else:
    return gcd(y % x, x)

# Miller Rabin 'probable prime' test
#
# returns 'False' if 'n' is definitely composite
# returns 'True' if 'n' is prime or probably prime
#
# 'r' is the number of trials performed

def miller_rabin(n, r = 10):
  t = n - 1
  s = 0
  while not t & 1:
    t >>= 1
    s += 1
  for i in range(r):
    a = random.randint(2, n - 1)
    x = pow(a, t, n)
    if x != 1 and x != n - 1:
      for j in range(s - 1):
        x = (x * x) % n
        if x == 1:
          return False
        if x == n - 1:
          break
      else:
        return False
  return True

# determine if n is probably prime - return
#    0 if n is 0, 1 or composite
#    1 if n is probably prime
#    2 if n is definitely prime

def probable_prime_p(nn, r):
  n = abs(nn)
  if n <= 2:
    return 2 if n == 2 else 0

  # trial division
  for p in prime_list(1000):
    if not n % p:
      return 2 if n == p else 0
    if p * p > n:
      return 2

  # Fermat test
  if pow(random.randint(2, n - 1), n - 1, n) != 1:
    return 0

  # Miller-Rabin test
  return 1 if miller_rabin(n, r) else 0

# count the number of lines in a file

def linecount(file_path):
  count = 0
  if not os.path.exists(file_path):
    die('can\'t open {0:s}'.format(file_path))
  with open(file_path, 'r') as in_file:
    for l in in_file:
      count += 1
  return count

# Read the log file to see if we've found all the prime
# divisors of N yet.

def get_primes(fact_p):

  with open(LOGNAME, 'r') as in_f:
    for l in in_f:
      l = chomp(l)
      m1 = re.search('r\d+=(\d+)\s+', l)
      if m1:
        val = int(m1.group(1))
        if len(val) > 1 and  len(val) < len(fact_p['ndivfree']):
          # Is this a prime divisor or composite?
          m2 = re.search('\(pp(\d+)\)', l)
          if m2:
            # If this is a prime we don't already have, add it.
            found = False
            for p in fact_p['primes']:
              if val == p:
                found = True
            if not found:
              fact_p['primes'].append(val)
          else:
            fact_p['comps'].append(val)

  # Now, try to figure out if we have all the prime factors:
  x = itertools.reduce(lambda x,y : x * y, fact_p['primes'], 1)
  if x == fact_p['ndivfree'] or probab_prime_p(fact_p['ndivfree'] // x, 10):
    if x != fact_p['ndivfree']:
      fact_p['primes'].append(fact_p['ndivfree'] // x)
    for p in fact_p['primes']:
      cs = '-> p: {0:s} (pp{1:d})'.format(val, len(val))
      output(cs)
    return True
  # Here, we could try to recover other factors by division,
  # but until we have a primality test available, this would
  # be pointless since we couldn't really know if we're done.
  return False

# The parameter degree, if nonzero, will let this function adjust
# parameters for SNFS factorizations with a predetermined polynomial
# of degree that is not the optimal degree.

nonPrefDegAdjust = 12

def load_default_parameters(nfs_type, digits, degree,
          fact_p, pols_p, lats_p, clas_p):

  if nfs_type == 'gnfs':
    lats_p['lss'] = 0
  if not os.path.exists(DEFAULT_PAR_FILE):
    die('Could not find default parameter file {0:s}!'
                                    .format(DEFAULT_PAR_FILE))
  with open(DEFAULT_PAR_FILE, 'r') as in_f:
    par_digits = 0
    par_degree = 0
    how_close = 1000
    for l in in_f:
      l = chomp(l)
      l = chomp_comment(l)
      l = remove_ws(l)
      if l:
        tu = l.split(',')
        t = tu[0]
        if t == nfs_type:
          o = 2
          cand_digits = int(tu[1])
          cand_degree = int(tu[o + 0])
          s1 = abs(cand_digits - digits)
          s2 = abs(cand_digits - nonPrefDegAdjust - digits) + nonPrefDegAdjust

          # try to properly handle crossover from degree 4 to degree 5
          if (s1 if nfs_type == 'gnfs' or not degree or degree == cand_degree
                  or par_degree == cand_degree - 1 else s2) < how_close:

            how_close = (s2 if nfs_type != 'gnfs' and degree
                                  and cand_degree != degree else s1)
            par_digits = cand_digits
            par_degree = cand_degree

            pols_p['maxs1'] = int(tu[o + 1])
            pols_p['maxskew'] = int(tu[o + 2])
            pols_p['goodscore'] = float(tu[o + 3])
            pols_p['examinefrac'] = float(tu[o + 4])
            pols_p['j0'] = int(tu[o + 5])
            pols_p['j1'] = int(tu[o + 6])
            pols_p['estepsize'] = int(tu[o + 7])
            pols_p['maxtime'] = int(tu[o + 8])

            lats_p['rlim'] = int(tu[o + 9])
            lats_p['alim'] = int(tu[o + 10])
            lats_p['lpbr'] = int(tu[o + 11])
            lats_p['lpba'] = int(tu[o + 12])
            lats_p['mfbr'] = int(tu[o + 13])
            lats_p['mfba'] = int(tu[o + 14])
            lats_p['rlambda'] = float(tu[o + 15])
            lats_p['alambda'] = float(tu[o + 16])
            lats_p['qintsize'] = int(tu[o + 17])

            clas_p['cl_a'] = int(tu[o + 18])
            clas_p['cl_b'] = int(tu[o + 19])

            fact_p['qstep'] = lats_p['qintsize']

  fact_p['digs'] = digits / 0.72 if nfs_type == 'gnfs' else digits
  # 0.72 is inspired by T.Womack's crossover 28/29 for GNFS-144 among other consideration

  if fact_p['digs'] >= 160:
    # the table parameters are easily splined; the table may be not needed at all --SB.
    lats_p['rlim'] = lats_p['alim'] = int(0.07 * 10 ** (fact_p['digs'] / 60.0) + 0.5) * 100000
    lats_p['lpbr'] = lats_p['lpba'] = int(21 + fact_p['digs'] / 25.0)
    lats_p['mfbr'] = lats_p['mfba'] = 2 * lats_p['lpbr'] - (1 if fact_p['digs'] < 190 else 0)
    lats_p['rlambda'] = lats_p['alambda'] = 2.5 if fact_p['digs'] < 200 else 2.6
    lats_p['qintsize'] = fact_p['qstep'] = 100000
    clas_p['cl_a'] = 4000000
    clas_p['cl_b'] = 400
    par_digits = digits

  pols_p['degree'] = par_degree
  print('-> Selected default factorization parameters for {0:d} digit level.'.
                            format(par_digits))
  if nfs_type == 'gnfs':
    r = (95, 110, 140, 158, 185, 999)
  else:
    if degree and par_degree != degree:
      digits += nonPrefDegAdjust
    r = (120, 150, 195, 240, 275, 999)

  i = 1
  for v in r:
    if digits < v:
      break
    i += 1
  else:
    die('You are joking?')

  lats_p['siever'] = re.sub('4I1[0-9]e', '4I1' + str(i) + 'e', 'gnfs-lasieve4I10e')
  output('-> Selected lattice siever: {0:s}'.format(lats_p['siever']))

# These are default parameters for polynomial selection using the
# Kleinjung/Franke tool.
# arg0 = number of digits in N.

def load_pol5_parameters(digits, pol5_p):

  par_digits = 0
  if NO_DEF_NM_PARAM or digits < 100:
    pol5_p['search_a5step'] = 1
    pol5_p['npr'] = int(digits / 13.0 - 4.5)
    pol5_p['npr'] = pol5_p['npr'] if pol5_p['npr'] > 4 else 4
    pol5_p['normmax'] = 10 ** (0.163  * digits - 1.4794)
    pol5_p['normmax1'] = 10 ** (0.1522 * digits - 1.6969)
    pol5_p['normmax2'] = 10 ** (0.142 * digits - 2.6429)
    pol5_p['murphymax'] = 10 ** (-0.0569 * digits - 2.8452)
    pol5_p['max_pst_time'] = int(0.000004 / pol5_p['murphymax'])
    output('-> Selected polsel parameters for {0:d} digit level.'.format(digits))
    return

  if not os.path.exists(DEFAULT_POLSEL_PAR_FILE):
    die('Could not find default parameter file {0:s}!'
                                .format(DEFAULT_POLSEL_PAR_FILE))

  with open(DEFAULT_POLSEL_PAR_FILE, 'r') as in_f:
    how_close = 1000
    for l in in_f:
      l = chomp(l)
      l = chomp_comment(l)
      l = remove_ws(l)
      if l:
        tu = l.split(',')
        d = int(tu[0])
        if abs(d - digits) < how_close:
          o = 1
          how_close = abs(d - digits)
          par_digits = d
          pol5_p['max_pst_time'] = 60 * int(tu[o + 0])
          pol5_p['search_a5step'] = int(tu[o + 1])
          pol5_p['npr'] = int(tu[o + 2])
          pol5_p['normmax'] = float(tu[o + 3])
          pol5_p['normmax1'] = float(tu[o + 4])
          pol5_p['normmax2'] = float(tu[o + 5])
          pol5_p['murphymax'] = float(tu[o + 6])

  output('-> Selected default polsel parameters for {0:d} digit level.'
                    .format(par_digits))

# The dictionary entries in this routine map each coefficient as a string
# to the coefficient value as floating point values. The (name, value)
# pairs on the BEGIN_POLY line are also entered into the dictionary for
# each polynomial

pname = ''

def terminate_pol5(x, y):
  die('Terminated on {0:s} by SIGINT'.format(pname))

def run_pol5(fact_p, pol5_p, lats_p, clas_p):
  global pname

  check_binary(POL51M0)
  check_binary(POL51OPT)
  projectname = NAME + '.polsel'
  host = socket.gethostname()
  pname = projectname + host + '.' + str(os.getpid())

  with open(pname + '.data', 'w') as out_f:
    print('N ' + str(fact_p['n']), file = out_f)

  pol5_term_flag = False
  old_handler = signal.signal(signal.SIGINT, terminate_pol5)

  load_pol5_parameters(fact_p['dec_digits'], pol5_p)
  pol5_p['max_pst_time'] *= polySelTimeMultiplier
  hmult = 1e3
  load_default_parameters('gnfs', fact_p['dec_digits'], 5,
              fact_p, pols_p, lats_p, clas_p)
  bestpolyinf = dict()
  bestpolyinf['Murphy_E'] = 0

  start_time = time.time()
  nerr = 0
  h_lo = 0
  while not pol5_term_flag and nerr < 2:
    h_hi = h_lo + pol5_p['search_a5step']

    output('-> Searching leading coefficients from {0:g} to {1:g}'
                      .format(h_lo * hmult + 1, h_hi * hmult))
    args = ('-b {0:s} -v -v -p {1:d} -n {2:g} -a {3:g} -A {4:g}'
                    .format(pname, pol5_p['npr'], pol5_p['normmax'], h_lo, h_hi))

    if not run_exe(POL51M0, args, out_file = pname + '.log'):

      # lambda-comp related errors can be skipped and some polys are
      # then found ull5-comp related are probably fatal, but let the
      # elapsed time.time() take care of them

      nerr = 0
      suc = grep_f('success', pname + '.log')
      changed = False
      if suc:
        args = ('-b {0:s} -v -v -n {1:g} -N {2:g} -e {3:g}'
                    .format(pname, pol5_p['normmax1'], pol5_p['normmax2'], pol5_p['murphymax']))
        ret = run_exe(POL51OPT, args, out_file = pname + '.log')
        if ret:
          die('Abnormal return value {0:d}. Terminating...'.format(ret))
        cat_f(pname + '.51.m', projectname + '.51.m.all')

        with open(pname + '.cand', 'r') as in_f:

          polyinf = dict()
          for l in in_f:
            l = chomp(l)
            if re.match('BEGIN POLY', l):
              l = re.sub('BEGIN POLY', '', l)
              l = re.sub('^ #', '', l)
              tu = l.split()
              for i in range(0, len(tu), 2):
                polyinf[tu[i]] = float(tu[i + 1])
            elif re.match('END POLY', l):
              if polyinf['Murphy_E'] > bestpolyinf['Murphy_E']:
                bestpolyinf = polyinf.copy()
                changed = True
                polyinf = dict()
            else:
              tu = l.split()
              polyinf[re.sub('^X', 'c', tu[0])] = int(tu[1])

        if changed:

          for key in sorted(bestpolyinf):
            print(key, ':', bestpolyinf[key])

          with open(NAME + '.poly', 'w') as out_f:

            print('name: {0:s}'.format(NAME), file = out_f)
            print('n: {0:d}'.format(fact_p['n']), file = out_f)

            for key in reversed(sorted(bestpolyinf)):
              if re.match('c\d+', key) or re.match('Y\d+', key):
                print('{0:s}: {1:d}'
                        .format(key, bestpolyinf[key]), file = out_f)
              elif re.match('skewness', key):
                print('skew: {0:<10.2f}'
                        .format(bestpolyinf[key]), file = out_f)
              elif key == 'M':
                print(key, bestpolyinf[key])
                print('# {0:s} {1:d}'
                        .format(key, bestpolyinf[key]), file = out_f)
              else:
                print('# {0:s} {1:g}'
                        .format(key, bestpolyinf[key]), file = out_f)

            print('type: {0:s}'.format('gnfs'), file = out_f)
            print('rlim: {0:d}'.format(lats_p['rlim']), file = out_f)
            print('alim: {0:d}'.format(lats_p['alim']), file = out_f)
            print('lpbr: {0:d}'.format(lats_p['lpbr']), file = out_f)
            print('lpba: {0:d}'.format(lats_p['lpba']), file = out_f)
            print('mfbr: {0:d}'.format(lats_p['mfbr']), file = out_f)
            print('mfba: {0:d}'.format(lats_p['mfba']), file = out_f)
            print('rlambda: {0:g}'.format(lats_p['rlambda']), file = out_f)
            print('alambda: {0:g}'.format(lats_p['alambda']), file = out_f)
            print('qintsize: {0:d}'.format(lats_p['qintsize']), file = out_f)

        cat_f(pname +'.cand', projectname + '.cand.all')
        delete_file(pname + '.cand')

      print('-> =====================================================')
      output('-> Best score so far: {0:g} (good_score={1:g})'
                .format(bestpolyinf['Murphy_E'], pol5_p['murphymax']))
      print('-> =====================================================')
      delete_file(pname + '.log')
      delete_file(pname + '.51.m')

    if time.time() > start_time + pol5_p['max_pst_time']:
      pol5_term_flag = True
    h_lo = h_hi

  delete_file(pname + '.data')
  signal.signal(signal.SIGINT, old_handler)

# We will start with a higher leading coefficient divisor. When it
# appears that we are searching in an interesting range, it will
# be backed down so that the resulting range can be searched with
# a finer resolution. This means that from time to time, the same
# poly will be found several times as we hone in on a region.

def run_poly_select(fact_p, pols_p, lats_p, clas_p):

  check_binary(POLYSELECT)
  lcd_choices = (2, 4, 4, 12, 12, 24, 24, 48, 48, 144, 144, 720, 5040)
  lcd_level = 4 + (fact_p['dec_digits'] - 70) // 10
  if lcd_level < 0:
    lcd_level = 0
  if lcd_level > 12:
    lcd_level = 12

  output('-> Starting search with leading coefficient divisor {0:d}'
              .format(lcd_choices[lcd_level]))

  load_default_parameters('gnfs', fact_p['dec_digits'], 0,
                    fact_p, pols_p, lats_p, clas_p)

  pols_p['maxtime'] *= polySelTimeMultiplier
  best_score = 0.0
  start_time = time.time()
  done = False
  best_lc = 1
  last_lc = 0
  multiplier = 0.75
  e_lo = 1

  while not done:
    e_hi = e_lo + pols_p['estepsize']

    lcd = lcd_choices[lcd_level]
    with open(NAME + '.polsel', 'w') as out_f:

      print('name: {0:s}'.format(NAME), file = out_f)
      print('n: {0:d}'.format(fact_p['n']), file = out_f)
      print('deg: {0:d}'.format(pols_p['degree']), file = out_f)
      print('bf: {0:s}.best.poly'.format(NAME), file = out_f)
      print('maxs1: {0:d}'.format(pols_p['maxs1']), file = out_f)
      print('maxskew: {0:d}'.format(pols_p['maxskew']), file = out_f)
      print('enum: {0:d}'.format(lcd), file = out_f)
      print('e0: {0:d}'.format(e_lo), file = out_f)
      print('e1: {0:d}'.format(e_hi), file = out_f)
      print('cutoff: {0:g}'.format(0.75 * pols_p['goodscore']), file = out_f)
      print('examinefrac: {0:g}'.format(pols_p['examinefrac']), file = out_f)
      print('j0: {0:d}'.format(pols_p['j0']), file = out_f)
      print('j1: {0:d}'.format(pols_p['j1']), file = out_f)

    args = '-if {0:s}.polsel'.format(NAME)
    ret = run_exe(POLYSELECT, args)
    if ret:
      die('Return value res. Terminating...'.format(ret))

    # Find the score of the best polynomial: E(F1,F2) =
    inp = True
    try:
      tmp = grep_f('E\(F1,F2\) =', NAME + '.best.poly')
    except IOError:
      inp = False

    if inp:
      score = tmp[0]
      score = float(re.sub('.*E\(F1,F2\) =', '', tmp[0]))
      tmp = grep_f('^c' + str(pols_p['degree']), NAME + '.best.poly')
      m = re.search('^c' + str(pols_p['degree']) + ':\s([\+\-]*\d*)', tmp[0])
      lc = int(m.group(1))
    else:
      score = 0.0
    if (score > multiplier * pols_p['goodscore'] and lc != best_lc
                    and  lc != last_lc ):
      multipler = 1.1 * multiplier if multiplier < 0.9 / 1.1 else multiplier
      last_lc = lc
      new_lcd_level = lcd_level - 1 if lcd > 0 else 0
      e_lo = e_lo * lcd_choices[lcd_level] // lcd_choices[new_lcd_level] - pols_p['estepsize']

      if lcd_level != new_lcd_level:
        print('-> Leading coefficient divisor dropped from {0:d} to {1:d}.'
                              .format(lcd_choices[lcd_level], lcd_choices[new_lcd_level]))
      lcd_level = new_lcd_level

    if score > best_score and lc != best_lc:
      best_score = score
      best_lc = lc
      last_best_time = time.time()
      os.rename(NAME + '.best.poly', NAME + '.thebest.poly')

      # We should now fill in the missing parameters with the default
      # loaded in from table. Do this now, so that the user has the
      # option to kill the script and still have a viable poly file.

      with open(NAME + '.thebest.poly', 'r') as in_f:
        with open(NAME + '.poly', 'w') as out_f:

          for l in in_f:
            l = chomp(l)
            if l.find('rlim:') != -1:
              l = 'rlim: {0:d}'.format(lats_p['rlim'])
            elif l.find('alim:') != -1:
              l = 'alim: {0:d}'.format(lats_p['alim'])
            elif l.find('lpbr:') != -1:
              l = 'lpbr: {0:d}'.format(lats_p['lpbr'])
            elif l.find('lpba:') != -1:
              l = 'lpba: {0:d}'.format(lats_p['lpba'])
            elif l.find('mfbr:') != -1:
              l = 'mfbr: {0:d}'.format(lats_p['mfbr'])
            elif l.find('mfba:') != -1:
              l = 'mfba: {0:d}'.format(lats_p['mfba'])
            elif l.find('rlambda:') != -1:
              l = 'rlambda: {0:g}'.format(lats_p['rlambda'])
            elif l.find('alambda:') != -1:
              l = 'alambda: {0:g}'.format(lats_p['alambda'])
            elif l.find('qintsize:') != -1:
              l = 'qintsize: {0:d}'.format(lats_p['qintsize'])
            if l:
              print(l, file = out_f)
          print('type: gnfs', file = out_f)

      delete_file(NAME + '.thebest.poly')
      delete_file(NAME + '.best.poly')

    print('-> =====================================================')
    output('-> Best score so far: {0:g} (good_score={1:g})     '
                          .format(best_score, pols_p['goodscore']))
    print('-> =====================================================')

    # We will allow another 5 minutes just in case there happens to
    # be a really good poly nearby (or the 'good_score' value was too low)
    if best_score > 1.4 * pols_p['goodscore']:
      done = (time.time() > last_best_time + 300)

    done |= (time.time() > start_time + pols_p['maxtime'])
    e_lo = e_hi

  output('-> Using poly with score={0:f}'.format(best_score))
  delete_file(NAME + '.polsel')

def fb_to_poly():
  with open(NAME + '.poly', 'w') as out_f:
    with open(NAME + '.fb', 'r') as in_f:
      for l in in_f:

        m = re.match('N\s+(\d+)', l)
        if m:
          print('n: {0:s}'.format(m.group(1)), file = out_f)

        m = re.match('SKEW\s+(\d*\.\d*)', l)
        if m:
          skew = float(m.group(1))

        m = re.match('R(\d+)\s+([+-]?\d+)', l)
        if m:
          print('Y{0:s}: {1:s}'.format(m.group(1),
                            m.group(2)), file = out_f)

        m = re.match('A(\d+)\s+([+-]?\d+)', l)
        if m:
          print('c{0:s}: {1:s}'.format(m.group(1),
                          m.group(2)), file = out_f)
    try:
      print('skew: {0:<10.2f}'.format(skew), file = out_f)
      print('type: gnfs', file = out_f)
    except:
      die('{0:s}.fb is not in the correct format'.format(NAME))

def run_msieve_poly(fact_p):

  with open(ININAME, 'w') as out_f:
    out_f.write('{0:d}'.format(fact_p['n']))
  if USE_CUDA:
    if run_msieve('-g {0:d} -v -np'.format(GPU_NUM)):
      die('Msieve Error: return value {0:d} - is CUDA enabled?. Terminating...'.format(ret))
  elif run_msieve('-v -np'):
    die('Msieve Error: return value {0:d}. Terminating...'.format(ret))
  if os.path.exists(FBNAME):
    fb_to_poly()
    return True
  else:
    return False

def change_parameters(lats_p):

  check_binary(MAKEFB)
  check_binary(PROCRELS)
  cs = ('-> Parameter change detected, dumping relations... ')
  output(cs)

  args = '-fb {0:s}.fb -prel {1:s} -dump'.format(NAME, RELSBIN)
  ret = run_exe(PROCRELS, args)
  if ret:
    die('Return value {0:d}. Terminating...'.format(ret))

  for f in glob.iglob(RELSBIN + '*'):
    delete_file(f)
  for f in glob.iglob('cols*'):
    delete_file(f)
  for f in glob.iglob('deps*'):
    delete_file(f)
  delete_file('factor.easy')
  for f in glob.iglob('lpindex*'):
    delete_file(f)
  for f in glob.iglob(NAME + '.*.afb.*'):
    delete_file(f)

  output('-> Making new factor base files...')
  args = ('-rl {0[rlim]:d} -al {0[alim]:d} -lpbr {0[lpbr]:d} -lpba {0[lpba]:d}'
          '{1:s} -of {2:s}.fb -if {2:s}.poly'.format(lats_p, LARGEPRIMES, NAME))
  ret = run_exe(MAKEFB, args)
  if ret:
    die('Return value {0:d}. Terminating...'.format(ret))

  output('-> Reprocessing siever output...')
  i = 0
  while os.path.exists('spairs.dump.i'):
    args = (' -fb {0:s}.fb -prel {1:s} -newrel spairs.dump.i -nolpcount'
                    .format(NAME, RELSBIN))
    ret = run_exe(PROCRELS, args)
    i = i + 1

  # Update the paramfile, used by this script to detect change
  # in parameter settings.
  with open(PARAMFILE, 'w') as out_f:
    print('rlim: {0:d}'.format(lats_p['rlim']), file = out_f)
    print('alim: {0:d}'.format(lats_p['alim']), file = out_f)
    print('lbpr: {0:s}'.format(LBPR), file = out_f)
    print('lbpa: {0:s}'.format(LBPA), file = out_f)

def check_for_parameter_change(lats_p):

  if not os.path.exists(PARAMFILE):

    output('-> Creating param file to detect parameter changes...')
    with open(PARAMFILE, 'w') as out_f:
      print('rlim: {0:d}'.format(lats_p['rlim']), file = out_f)
      print('alim: {0:d}'.format(lats_p['alim']), file = out_f)
      print('lpbr: {0:d}'.format(lats_p['lpbr']), file = out_f)
      print('lpba: {0:d}'.format(lats_p['lpba']), file = out_f)
    return

  # Okay - it exists. We should check it to see if the
  # parameters are the same as the current ones.
  with open(PARAMFILE, 'r') as in_f:
    old_params = in_f.readlines()

  tmp = grep_l('rlim:', old_params)
  old_rlim = int(re.sub('.*rlim:', '', tmp[0]))
  tmp = grep_l('alim:', old_params)
  old_alim = int(re.sub('.*alim:', '', tmp[0]))
  tmp = grep_l('lpbr:', old_params)
  old_lpbr = int(re.sub('.*lpbr:', '', tmp[0]))
  tmp = grep_l('lpba:', old_params)
  old_lpba = int(re.sub('.*lpba:', '', tmp[0]))
  if (old_rlim != lats_p['rlim'] or old_alim != lats_p['alim'] or
      old_lpbr != lats_p['lpbr'] or old_lpba != lats_p['lpba']):
    change_parameters(lats_p)
  else:
    output('-> No parameter change detected, resuming... ')

def plot_lp():

  if CHECK_BINARIES:
    if not os.path.exists(PLOT):
      return

  if not os.path.exists(LOGNAME):
    return

  with open(LOGNAME, 'r') as in_f:
    with open('.lprels', 'w') as out_f:
      print('0, 0', file = out_f)
      with  open('.rels', 'w') as out_rels:
        print('0, 0', file = out_rels)

        for l in in_f:
          l = str.upper(chomp(l))
          m = re.search('LARGEPRIMES')
          if m:
            l = re.sub('\[.*]\s*','', l)                     # strip date
            l = re.sub('(LARGEPRIMES: |RELATIONS: )', '', l) # strip the labels
            l = remove_ws(l)                                 # remove whitespace
            tu = l.split(',')
            print('{0:s}, {1:d}'.format(tu[1], int(tu[0]) - int(tu[1])), FILE = outf)

          m = re.search('FINALFF')
          if m:
            l = re.sub('\[.*]\s*','', l)                     # strip date
            l = re.sub('(LARGEPRIMES: |RELATIONS: )', '', l) # strip the labels
            l = remove_ws(l)                                 # remove whitespace
            tu = l.split(',')
            print('{0:s}, {1:s}'.format(tu[0], tu[1]), file = out_rels)

  os.putenv('XAXIS', 'Total relations')
  os.putenv('YAXIS', '')
  args = 'xprimes.png \'ExcessLargePrimes\' .lprels'
  ret = run_exe(PLOT, args)
  if ret:
    die('Return value {0:d}. Terminating...'.format(ret))

  os.putenv('XAXIS', 'Total relations')
  os.putenv('YAXIS', 'Full relation-sets')
  args = 'relations.png \'TotalFF\' .rels'
  ret = run_exe(PLOT, args)
  if ret:
    die('Return value {0:d}. Terminating...'.format(ret))

  delete_file('.lprels')
  delete_file('.rels')

class is_missing(Exception):
  def __init__(self, x):
    self.value = x
  def __str__(self):
    return self.value

def check_parameters(fact_p, poly_p, lats_p):

  check_binary(MSIEVE)
  check_binary(lats_p['siever'])  
  if CHECK_BINARIES:
    delete_file('.lprels')
    delete_file('.rels')
    with open('.rels', 'w') as out_f:
      print('{0:d}'.format(fact_p['n']), file = out_f)
    delete_file('.lprels')
    delete_file('.rels')

  if not fact_p['n']:
    die('Error: \'n\' not supplied!')
  if not (poly_p['m'] or 'Y1' in poly_p['coeff']):
    die('Error: \'m\' not supplied!')
  if not 'c' + str(poly_p['degree']) in poly_p['coeff']:
    die('Error: polynomial not supplied!')
  if not poly_p['skew']:
    poly_p['skew'] = (abs( poly_p['coeff']['c0'] / poly_p['coeff']['c'
                    + str(poly_p['degree'])]) ** (1.0 / poly_p['degree']))
    print('-> Using calculated skew {0:<10.2f}'.format(poly_p['skew']))

  try :
    if not lats_p['rlim']: raise is_missing('rlim')
    if not lats_p['alim']: raise is_missing('alim')
    if not lats_p['lpbr']: raise is_missing('lpbr')
    if not lats_p['lpba']: raise is_missing('lpba')
    if not lats_p['mfbr']: raise is_missing('mfbr')
    if not lats_p['mfba']: raise is_missing('mfba')
    if not lats_p['rlambda']: raise is_missing('rlambda')
    if not lats_p['alambda']: raise is_missing('alambda')
    if not fact_p['qstep']: raise is_missing('qstep')
  except is_missing as x:
    die('Error: \'' + str(x) + '\' not supplied!')

def get_parm_int(data, match):
  tmp = grep_l('^' + match + ':', data)
  if tmp:
    m = re.search('^' + match + ':\s*(-?\d+)', tmp[0])
    if m:
      return int(m.group(1))
  return None

# Read default parameters first. Then we will just override
# by any user-supplied parameters.

def read_parameters(fact_p, poly_p, lats_p):

  with open(NAME + '.poly', 'r') as in_f:
    file_lines = in_f.readlines()

  fact_p['n'] = get_parm_int(file_lines, 'n')
  fact_p['dec_digits'] = len(str(fact_p['n']))

  # Find the polynomial degree.
  coefvals = dict()
  coeff_lines = grep_l('^c\d+:', file_lines)
  d = 0
  for l in coeff_lines:
    # Grab the coefficient index
    # First char of line 'c' followed by a digit string.
    m = re.search('^c(\d+):\s*(-?\d+)', l)
    if m:
      key = int(m.group(1))
      val = int(m.group(2))
      if key > d:
        d = key
      if key in coefvals:
        print('-> Warning: redefining c{0:d}'.format(key))
    coefvals[key] = val

  poly_p['degree'] = get_parm_int(file_lines, 'deg')
  if not poly_p['degree']:
    poly_p['degree'] = d
  if poly_p['degree'] != d:
    print('-> Error: poly file specifies degree {0:d} but highest poly'
                                                .format(poly_p['degree']))
    print('->   coefficient given is c{0:d}!'.format(d))
    sys.exit(-1)

  for i in range(d):
    if i not in coefvals:
      coefvals[i] = 0

  commonfac = 0
  first = True
  for key in reversed(sorted(coefvals)):
    if first:
      commonfac = coefvals[key]
      first = False
    else:
      commonfac = gcd(commonfac, coefvals[key])

  if CHECK_POLY and commonfac > 1:
    print('-> Error: poly coefficients have a common factor commonfac.'
            ' Please divide it out.')
    sys.exit(-1)

  denom = get_parm_int(file_lines, 'Y1')
  numer = get_parm_int(file_lines, 'Y0')
  poly_p['m'] = get_parm_int(file_lines, 'm')

  if denom and numer:
    if denom < 0:
      denom = -denom
    else:
      numer = -numer
    #    print '-> Common root is numer / denom\n'
    # paranoia if CHECK_POLY is set

    if CHECK_POLY:
      cf = gcd(numer, denom)
      if cf != 1:
        print('-> Error: {0:d} and {1:d} have a common factor {2:d}.'
                  ' Please divide it out.'.format(denom, numer, cf))
        sys.exit()

    if CHECK_POLY and poly_p['m'] and (denom * poly_p['m'] - numer) % fact_p['n']:
      print('-> Error: {0:d} * {1:d} + {2:d} != 0 mod {0:d}!'
                  .format(denom, poly_p['m'], numer, fact_p['n']))
      sys.exit(-1)

  polyval = 0
  if denom and numer:
    for i in range(poly_p['degree'] + 1):
      polyval += coefvals[i] * numer ** i * denom ** (poly_p['degree'] - i)
  elif poly_p['m']:
    #    print('-> Common root is {0:d}'.format(poly_p['m']))
    for i in range(poly_p['degree'], -1, -1):
      polyval = poly_p['m'] * polyval + coefvals[i]

  if CHECK_POLY and polyval == 0:
    print('-> Warning: evaluated polynomial value polyval is negative or zero.')
    print('->   This is at least a little strange.')

  if CHECK_POLY and polyval % fact_p['n'] != 0:
    print('-> Error: evaluated polynomial value polyval is not a multiple of n!')
    sys.exit(-1)

  #  print '-> Evaluated value is polyval\n'

  tmp = grep_l('type:', file_lines)
  m = re.search('.*type:\s+(gnfs|snfs)', tmp[0])
  if not m:
    print('-> Error: poly file should contain one of the following lines:')
    print('-> type: snfs')
    print('-> type: gnfs')
    print('-> Please add the appropriate line and re-run.')
    sys.exit(-1)
  elif m.group(1) == 'gnfs':
    fact_p['type'] = 'gnfs'
    load_default_parameters('gnfs', fact_p['dec_digits'], poly_p['degree'],
                      fact_p, pols_p, lats_p, clas_p)
  else:
    fact_p['type'] = 'snfs'
    # We need the difficulty level of the number, which may be
    # noticably larger than the number of digits.
    fact_p['snfs_difficulty'] = len(str(polyval)) # + math.log(int(str(polyval)[0:1])) - 1
    print('-> SNFS_DIFFICULTY is about {0:d}.'.format(fact_p['snfs_difficulty']))
    load_default_parameters('snfs', fact_p['snfs_difficulty'], poly_p['degree'],
                      fact_p, pols_p, lats_p, clas_p)

  # Now look for user-supplied parameters.
  fact_p['q0'] = 0
  with open(NAME + '.poly', 'r') as in_f:
    for l in in_f:
      l = chomp(l)
      l = chomp_comment(l)
      l = remove_ws(l)
      if len(l) and l.find(':') != - 1:
        token, val = l.split(':')
        if len(token) > 0 and len(val) > 0:
          if token == 'n':
            fact_p['n'] = int(val)
          elif token == 'm':
            poly_p['m'] = int(val)
          elif token == 'rlim':
            lats_p['rlim'] = int(val)
          elif token == 'alim':
            lats_p['alim'] = int(val)
          elif token == 'lpbr':
            lats_p['lpbr'] = int(val)
          elif token == 'lpba':
            lats_p['lpba'] = int(val)
          elif token == 'mfbr':
            lats_p['mfbr'] = int(val)
          elif token == 'mfba':
            lats_p['mfba'] = int(val)
          elif token == 'rlambda':
            lats_p['rlambda'] = float(val)
          elif token == 'alambda':
            lats_p['alambda'] = float(val)
          elif token == 'knowndiv':
            fact_p['knowndiv'] = int(val)
          elif token == 'skew':
            poly_p['skew'] = float(val)
          elif token == 'q0':
            fact_p['q0'] = int(val)
          elif token == 'qintsize':
            lats_p['qintsize'] = int(val)
          elif token == 'lss':
            lats_p['lss'] = val
          else:
            m = re.search('(c|Y).', token)
            if m :
              poly_p['coeff'][token] = int(val)

  fact_p['qstep'] = lats_p['qintsize']
  if fact_p['knowndiv']:
    if fact_p['n'] % fact_p['knowndiv']:
      die('-> Error: knowndiv {0:d} does not divide {0:d}!'
                       .format(fact_p['knowndiv'], fact_p['n']))
    fact_p['ndivfree'] = fact_p['n'] // fact_p['knowndiv']
    fact_p['n'] = fact_p['ndivfree']
  else:
    fact_p['ndivfree'] = fact_p['n']

  if probable_prime_p(fact_p['ndivfree'], 10):
    die('-> Error: {0:d} is probably prime!'.format(fact_p['n']))
  if fact_p['q0'] == 0:
    fact_p['q0'] = (lats_p['rlim'] if lats_p['lss'] else lats_p['alim']) // 2
  fact_p['qstart'] = fact_p['q0']
  check_for_parameter_change(lats_p)

# sieving intervals are triples (q_start, q_pos, q_end) that
# are kept in a Python deque list in fact_p['q_dq']. In each
# sieving step, the q interval (q0 .. q0 + qstep) is divided
# into sub-intervals for sieving by the available threads on
# this machine.   When this step is completed, the intervals
# are updated for the next step.

# When termainated by a user interrupt the siever will write
# a file named 'LASTSPQ<N>', with <N> = 100 * PNUM + TNUM if
# multi-threaded or PNUM if single threaded (thread number =
# TNUM, processor number = PNUM).  This gives the q position
# when the siever was stopped.  These files from each thread
# are used to create a file, JOBNAME.resume, that is used to
# restart the sieving.  It has the fileds:
#
# Q0:       the Q0 value when terminated
# QSTEP:    the QSTEP value when terminated
# QQ<N>:    the sieving interval (ql, qp, qh)
#           for thread<N> when it was stopped

# The following three routines manipulate sieve intervals
# and are collected together here to assist in further
# improvements. The algorithms are primitive right now.

def init_q_dq(fact_p, n_threads, qbase):
  inc = int(fact_p['qstep'] // n_threads)
  for j in range(n_threads):
    if j >= len(fact_p['q_dq']):
      fact_p['q_dq'].append(0)
    if not fact_p['q_dq'][j]:
      fact_p['q_dq'][j] = ((qbase, qbase, qbase + inc))
      qbase += inc

def update_q_dq(fact_p, n_threads, n_clients):
  for j in range(n_threads):
    ql, qp, qh = fact_p['q_dq'].popleft()
    ql += n_clients * fact_p['qstep']
    qh += n_clients * fact_p['qstep']
    fact_p['q_dq'].append((ql, ql, qh))

def divide_q_dq(fact_p, n_threads):
  while len(fact_p['q_dq']) < n_threads:
    ql, qp, qh = fact_p['q_dq'].popleft()
    t = int((qh - qp) // 2)
    fact_p['q_dq'].append((ql, qp, qp + t))
    fact_p['q_dq'].append((ql, qp + t, qh))

def write_resume_file(n_threads, fact_p):
  with open(JOBNAME + '.resume', 'w') as out_f:
    if 'q0' in fact_p:
      print('Q0: {0:d}'.format(fact_p['q0']), file = out_f)
    if 'qstep' in fact_p:
      print('QSTEP: {0:d}'.format(fact_p['qstep']), file = out_f)
    for j in range(n_threads):
      ql, qp, qh = fact_p['q_dq'][j]
      print('QQ{0:d}: {1:d}, {2:d}, {3:d}'
          .format(j, ql, qp, qh), file = out_f)

def read_resume_file():
  rn = JOBNAME + '.resume'
  fact_p['q_dq'].clear()
  with open(rn, 'r') as in_f:
    tmp = in_f.readlines()
    for l in tmp:
      m = re.search('Q0:\s+(\d+)', l)
      if m:
        q0 = int(m.group(1))
      m = re.search('QSTEP:\s+(\d+)', l)
      if m:
        qstep = int(m.group(1))
      m = re.search('QQ(\d+):\s*(\d+),\s*(\d+),\s*(\d+)', l)
      if m:
        while int(m.group(1)) >= len(fact_p['q_dq']):
          fact_p['q_dq'].append(0)
        fact_p['q_dq'][int(m.group(1))] = (int(m.group(2)),
                int(m.group(3)), int(m.group(4)))
  return (q0, qstep)

def setup(fact_p, poly_p, lats_p, client, n_clients, n_threads):

  # Should we resume from an earlier run? #
  resume = os.path.exists(JOBNAME + '.resume')

  if resume:
    if PROMPTS:
      ip = ('-> It appears that an earlier attempt was interrupted. Resume? (y/n) ')
      while True:
        if sys.version_info[0] < 3:
          r = raw_input(ip)
        else:
          r = input(ip)

        if r == 'y' or r == 'Y':
          resume = True
          break
        elif r == 'n' or r == 'N':
          resume = False
          break

  if fact_p['type'] == 'gnfs':
    if lats_p['lpbr'] == 25:
      lats_p['minrels'] = int(38000.0 * (fact_p['dec_digits'] - 47))
    elif lats_p['lpbr'] == 26:
      lats_p['minrels'] = int(91000.0 * (fact_p['dec_digits'] - 55))
    elif lats_p['lpbr'] == 27:
      lats_p['minrels'] = int(150000.0 * (fact_p['dec_digits'] - 61))
    elif lats_p['lpbr'] == 28:
      lats_p['minrels'] = int(440000.0 * (fact_p['dec_digits'] - 89))
    else:
      lats_p['minrels'] = int(10.0 ** (fact_p['dec_digits'] / 41.0 + 4.0))
  else:
    lats_p['minrels'] = int(10.0 ** (fact_p['digs'] / 70.0 + 4.6))
# lats_p['minrels'] = int(0.2 * 1.442695 *((2 ** lats_p['lpba']) /lats_p['lpba'] + (2 ** lats_p['lpbr']) / lats_p['lpbr']))
  output('-> Estimated minimum relations needed: {0:g}'.format(1.0 * lats_p['minrels']))

  # Setup the parameters for sieving ranges. #
  if not resume:
    if client_id == 1:
      if os.path.exists(NAME + '.n') and not os.path.exists(NAME + '.poly'):
        delete_file(LOGNAME)
      output('-> cleaning up before a restart')

      # Clean up any junk leftover from an earlier attempt.
      for f in glob.iglob('cols*'):
        delete_file(f)
      for f in glob.iglob('deps*'):
        delete_file(f)
      delete_file('factor.easy')
      for f in glob.iglob('lpindex*'):
        delete_file(f)
      for f in glob.iglob(RELSBIN + '*'):
        delete_file(f)
      delete_file('spairs.out')
      delete_file('spairs.out.gz')
      delete_file(NAME + '.fb')
      for f in glob.iglob('*.afb.0'):
        delete_file(f)
      for f in glob.iglob('*.afb.1'):
        delete_file(f)
      delete_file('.params')

      # Was a discriminant divisor supplied?
      if fact_p['dd']:
        with open(LOGNAME, 'a') as out_f:
          print('{0:d}'.format(fact_p['dd']), file = out_f)

      # Create msieve file
      with open(ININAME, 'w') as out_f:
        print('{0:d}'.format(fact_p['n']), file = out_f)

      with open(DATNAME, 'w') as out_f:
        print('N {0:d}'.format(fact_p['n']), file = out_f)

      with open(FBNAME, 'w') as out_f:
        print('N {0:d}'.format(fact_p['n']), file = out_f)
        print('SKEW {0:<10.2f}'.format(poly_p['skew']), file = out_f)

        if not 'Y1' in poly_p['coeff']:
          poly_p['coeff']['Y1'] = 1
          poly_p['coeff']['Y0'] = -poly_p['m']

        for key in reversed(sorted(poly_p['coeff'])):
          if key[0] == 'c':
            print('A{0:d} {1:d}'.format(int(key[1:]), poly_p['coeff'][key]), file = out_f)

        print('R1 {0:d}'.format(poly_p['coeff']['Y1']), file = out_f)
        print('R0 {0:d}'.format(poly_p['coeff']['Y0']), file = out_f)
        print('FAMAX {0:d}'.format(lats_p['alim']), file = out_f)
        print('FRMAX {0:d}'.format(lats_p['rlim']), file = out_f)
        print('SALPMAX {0:d}'.format(2 ** lats_p['lpba']), file = out_f)
        print('SRLPMAX {0:d}'.format(2 ** lats_p['lpbr']), file = out_f)
    fact_p['q0'] = fact_p['qstart']
    fact_p['q_dq'].clear()

  else:

    fact_p['q0'] = 0
    try:
      t = read_resume_file()
      fact_p['q0'], fact_p['qstep'] = t
      output('-> resuming a block for q from {0:d} to {1:d}'
          .format(fact_p['q0'], fact_p['q0'] + fact_p['qstep']))
    except IOError:
      print('-> Could not determine a starting q value!')
      print('-> Please enter a starting point for the special q: ')
      if sys.version_info[0] < 3:
        tmp = raw_input()
      else:
          tmp = input()
      fact_p['q0'] = int(remove_ws(chomp(tmp)))
      if not fact_p['q0']:
        fact_p['q0'] = fact_p['qstart']
      fact_p['q_dq'].clear()

  # add sieve intervals if the sieve interval queue is not long enough
  if 0 < len(fact_p['q_dq']) < n_threads:
    divide_q_dq(fact_p, n_threads)
  else:
    t_q = int(fact_p['q0'] + ((client - 1) % n_clients) * fact_p['qstep'])
    init_q_dq(fact_p, n_threads, t_q)

def job_out0(sieve_lim, lats_p, out_f):

  print('rlim: {0:d}'.format(sieve_lim[1]), file = out_f)
  print('alim: {0:d}'.format(sieve_lim[0]), file = out_f)
  print('lpbr: {0:d}'.format(lats_p['lpbr']), file = out_f)
  print('lpba: {0:d}'.format(lats_p['lpba']), file = out_f)
  print('mfbr: {0:d}'.format(lats_p['mfbr']), file = out_f)
  print('mfba: {0:d}'.format(lats_p['mfba']), file = out_f)
  print('rlambda: {0:g}'.format(lats_p['rlambda']), file = out_f)
  print('alambda: {0:g}'.format(lats_p['alambda']), file = out_f)

def job_out1(q0, q1, out_f):
  print('q0: {0:d}'.format(q0), file = out_f)
  print('qintsize: {0:d}'.format(q1 - q0), file = out_f)
  print('#q1:{0:d}'.format(q1), file = out_f)

def job_out2(clas_p, out_f):
  print('a0: {0:s}'.format(clas_p['a0']), file = out_f)
  print('a1: {0:s}'.format(clas_p['a1']), file = out_f)
  print('b0: {0:s}'.format(clas_p['b0']), file = out_f)
  print('b1: {0:s}'.format(clas_p['b1']), file = out_f)

def make_sieve_jobfile(FNAME, fact_p, poly_p, lats_p, clas_p = None):

  q0 = fact_p['q0']
  sieve_type = 1 if q0 > 0 or fact_p['qstep'] > 0 else 0

  sieve_lim = [lats_p['alim'], lats_p['rlim'], None]
  if sieve_type == 1:
    if lats_p['lss'] and lats_p['rlim'] > q0:
      sieve_lim[1] = q0 - 1
      sieve_lim[2] = '.afb.1'
    elif not lats_p['lss'] and lats_p['alim'] > q0:
      sieve_lim[0] = q0 - 1
      sieve_lim[2] = '.afb.0'

  for  j in range(SV_THREADS):
    ql, qp, qh = fact_p['q_dq'][j]
    t_fname = FNAME + '.T' + str(j)
    delete_file(t_fname)

    output('-> making sieve job for q = {1:d} in {0:d} .. {2:d} as file {3:s}'
                        .format(ql, qp, qh, t_fname))

    with open(t_fname, 'w') as out_f:

      print('n: {0:d}'.format(fact_p['n']), file = out_f)
      if poly_p['m']:
        print('m: {0:d}'.format(poly_p['m']), file = out_f)

      # The polynomial coefficients:
      for key in reversed(sorted(poly_p['coeff'])) :
        print('{0:s} {1:d}'.format(key + ':', poly_p['coeff'][key]), file = out_f)

      print('skew: {0:<10.2f}'.format(poly_p['skew']), file = out_f)

      job_out0(sieve_lim, lats_p, out_f)
      if sieve_type == 1:
        job_out1(qp, qh, out_f)
      else:
        job_out2(clas_p, out_f)

    if sieve_lim[2]:
      delete_file(t_fname + sieve_lim[2])

  return sieve_lim[2]

# arg0 = A value, to sieve [-A,A]
# arg1 = B0
# arg2 = B1, to sieve for b values in [B0, B1].

def run_classical_sieve(a, b0, b1):
  if not DOCLASSICAL:
    return

  max_b = 0
  lastline = 0

  # First, scan the line file and find the largest b-value that was sieved.
  line_file = DATNAME + '.line'

  if os.path.exists(line_file):
    with open(line_file, 'r') as in_f:
      tmp = in_f.readline()
      tmp = in_f.readline()
    bb = int(chomp(tmp))
    max_b = bb if bb > max_b else max_b

  max_b = b0 if max_b < b0 else max_b
  if max_b < b1:

    with open(FBNAME, 'a') as out_f:
      print('SLINE {0:d}'.format(a), file = out_f)

    print('-> Line file scanned: resuming classical sieve from b = {0:d}.'
                        .format(max_b))
    if run_msieve('-t {0:d} -ns {1:d},{2:d}'.format(LA_THREADS, max_b, b1)):
      die('Interrupted. Terminating...')

def log_sieve_time(val) :
  write_string_to_log('LatSieveTime: {0:g}'.format(val))

procs = []  # list of thread popen instances

def terminate_siever(x, y):
  global procs
  for p in procs:
    if p.poll() == None:
      p.terminate()
  print('siever terminated')

def read_spq(fact_p):
  for j in range(SV_THREADS):
    ql, qp, qh = fact_p['q_dq'][j]
    try:
      with open('.last_spq' + str(100 * PNUM + j), 'r') as in_f:
        tmp = remove_ws(chomp(in_f.readline()))
        if tmp:
          t = int(chomp(tmp))
          if t > qp:
            fact_p['q_dq'][j] = (ql, t, qh)
    except IOError:
      pass

def monitor_sieve_threads(delay = 1.0):
  global procs
  ret = 0
  running = True
  while running:
    read_spq(fact_p)
    try:
      if delay:
        time.sleep(delay)
    except:
      pass
    running = False
    for p in procs:
      retc = p.poll()
      if retc == None:
        running = True
      else:
        ret |= retc
  return ret

def run_siever(client_id, n_clients, n_threads, fact_p, lats_p):
  global procs
  old_handler = signal.signal(signal.SIGINT, terminate_siever)

  siever_option = '-r' if lats_p['lss'] else '-a'
  siever_side = 'rational' if lats_p['lss'] else 'algebraic'
  output('-> entering sieving loop')

  while not os.path.exists(COLSNAME):

    sieve_lim = make_sieve_jobfile(JOBNAME, fact_p, poly_p, lats_p)

    if fact_p['q0'] >= 2 ** lats_p['lpba']:
      print('-> {0:s} : Severe error!'.format(NAME))
      print('->     Current special q = {0:s} has exceeded max. large alg. prime = {1:d)!'
                        .format(fact_p['q0'], 2 ** lats_p['lpba']))
      print('-> You can try increasing LPBA, re-launch this script and cross your fingers.')
      print('-> But be aware that if you\'re seeing this, your factorization is taking')
      print('-> much longer than it would have with better parameters.')
      sys.exit(-1)

    write_resume_file(n_threads, fact_p)
    output('-> Lattice sieving {0:s} q from {1:d} to {2:d}.'
              .format(siever_side, fact_p['q0'], fact_p['q0'] + fact_p['qstep']))
    start_time = time.time()

    for j in range(n_threads):
      sn = SIEVER_OUTPUTNAME + '.T' + str(j)
      delete_file(sn)
      args = ('-k -o {0:s} -v -n{1:d} {2:s} {3:s}'
         .format(sn, 100 * PNUM + j, siever_option, JOBNAME + '.T' + str(j)))
      procs.append(run_exe(lats_p['siever'], args, wait = False))

    ret = monitor_sieve_threads()
    procs = []

    for j in range(n_threads):
      if sieve_lim:
        delete_file(JOBNAME + '.T' + str(j) + sieve_lim)
      cat_f(SIEVER_OUTPUTNAME + '.T' + str(j), SIEVER_OUTPUTNAME)
      delete_file(SIEVER_OUTPUTNAME + '.T' + str(j))

    if ret and ret != -1073741819:

      output('-> Return value {0:d}. Updating job file and terminating...'
                                .format(ret))
      cat_f(SIEVER_OUTPUTNAME, SIEVER_ADDNAME)
      delete_file(SIEVER_OUTPUTNAME)

      write_resume_file(n_threads, fact_p)
      # Record the time to the logfile.
      log_sieve_time(time.time() - start_time)
      die('Terminating...')
    else:
      fact_p['q0'] += n_clients * fact_p['qstep']
      update_q_dq(fact_p, n_threads, n_clients)
      write_resume_file(0, fact_p)

    if not os.path.exists(SIEVER_OUTPUTNAME):
      die('Some error ocurred and no relations were found! Examing log file.')

    if client_id > 1:
      cat_f(SIEVER_OUTPUTNAME, SIEVER_ADDNAME)
      delete_file(SIEVER_OUTPUTNAME)
    else:
      # Are there relations coming from somewhere else which should be added in?
      if os.path.exists(SIEVER_ADDNAME):
        cat_f(SIEVER_ADDNAME, SIEVER_OUTPUTNAME)
        delete_file(SIEVER_ADDNAME)

      for i in range(n_clients):
        san = 'spairs.add.' + str(i + 1)
        if os.path.exists(san):
          cat_f(san, SIEVER_OUTPUTNAME)
          delete_file(san)
          
      cat_f(SIEVER_OUTPUTNAME, DATNAME)
      if SAVEPAIRS:
        gzip_f(SIEVER_OUTPUTNAME, 'spairs.save.gz')
      delete_file(SIEVER_OUTPUTNAME)

      if os.path.exists('minrels.txt'):
        with open('minrels.txt', 'r') as in_f:
          tmp = in_f.readline()
        m = re.search('(\d+)', tmp)
        if m:
          lats_p['minrels'] = int(m.group(1))

      lats_p['currels'] = curr_rels = linecount(DATNAME)
      pc = (100.0 * curr_rels) / lats_p['minrels']
      output('Found {0:d} relations, {1:2.1f}% of the estimated minimum ({2:d}).'
                            .format(curr_rels, pc, lats_p['minrels']))
      if curr_rels > lats_p['minrels']:
        if run_msieve('-t {0:d} -nc1'.format(LA_THREADS)):
          die('Return value {0:d}. Terminating...'.format(ret))

    for j in range(n_threads):
      delete_file(JOBNAME + '.T' + str(j))
    log_sieve_time(time.time() - start_time)

  fact_p['last_spq'] = dict()
  delete_file(JOBNAME + '.resume')
  signal.signal(signal.SIGINT, old_handler)

def summary_name(name, fact_p):
  if fact_p['type'] == 'gnfs':
    s = 'g' + str(fact_p['dec_digits'])
  else :
    s = 's' + str(fact_p['snfs_difficulty'])
  t = os.path.split(name)
  return os.path.join(t[0], s + '-' + t[1] + '.txt')
  
def output_summary(name, fact_p, pols_p, poly_p, lats_p):
  
  # Set the summary file name
  sum_name = summary_name(name, fact_p)
  
  # Figure the time scale for this machine.
  output('-> Computing {0:g} scale for this machine...'.format(time.time()))
  (ret, res) = run_exe(PROCRELS, '-speedtest', out_file = subprocess.PIPE)
  tmp = grep_l('timeunit:', res)
  timescale = float(re.sub('timeunit:\s*', '', tmp[0]))
  
  # And gather up some stats.
  sieve_time = 0.0
  relproc_time = 0.0
  matrix_time = 0
  sqrt_time = 0
  min_q = max_q = 0
  prunedmat = rels = ''
  rprimes = aprimes = 0
  version = 'Msieve-1.40'

  with open(LOGNAME, 'r') as in_f:

    for l in in_f:
      l = chomp(l)
      l = re.sub('\s+$', '', l)
      tu = l.split()

      m = re.search('for q from (\d+) to (\d+) as file', l)
      if m:
        t = int(m.group(1))
        min_q = t if t < min_q or not min_q else min_q
        t = int(m.group(2))
        max_q = t if t > max_q or not max_q else max_q

      m = re.search('LatSieveTime:\s*(\d+)', l)
      if m:
        sieve_time += float(m.group(1))

      m = re.search('(Msieve.*)$', l)
      if m:
        version = m.group(1)

      m = re.search('RelProcTime: (\S+)', l)
      if m:
        relproc_time += int(m.group(1))

      m = re.search('BLanczosTime: (\S+)', l)
      if m:
        matrix_time += int(m.group(1))

      m = re.search('sqrtTime: (\S+)', l)
      if m:
        sqrt_time += int(m.group(1))

      m = re.search('rational ideals', l)
      if m:
        rprimes = str(tu[6]) + ' ' + str(tu[7]) + ' ' + str(tu[5])

      m = re.search('algebraic ideals', l)
      if m:
        aprimes = str(tu[6]) + ' ' + str(tu[7]) + ' ' + str(tu[5])

      m = re.search('unique relations', l)
      if m:
        rels = str(tu[-3]) + ' ' + str(tu[-1])

      m = re.search('matrix is', l)
      if m:
        prunedmat = str(tu[7]) + ' x ' + str(tu[9])

      m = re.search('prp', l)
      if m:
        tmp = int(re.sub('.*factor: ', '', l))
        if 1 < len(str(tmp)) < fact_p['dec_digits']:
          fact_p['divisors'].append(tmp)

  with open('ggnfs.log', 'a') as out_f:
    print('Number: {0:s}'.format(NAME), file = out_f)
    print('N = {0:d}'.format(fact_p['n']), file = out_f)
    for dd in sorted(set(fact_p['divisors'])):
      print('factor: {0:d}'.format(dd), file = out_f)

  # Convert times from seconds to hours.
  sieve_time /= 3600.0
  relproc_time /= 3600.0
  matrix_time /= 3600.0
  sqrt_time /= 3600.0
  total_time = sieve_time + relproc_time + matrix_time + sqrt_time + psTime

  with open(sum_name, 'w') as out_f:
    print('Number: {0:s}'.format(NAME), file = out_f)
    print('N = {0:d} ({1:d} digits)'.format(fact_p['n'], fact_p['dec_digits']), file = out_f)

    if fact_p['type'] == 'snfs':
      print('SNFS difficulty: {0:d} digits.'.format(fact_p['snfs_difficulty']), file = out_f)

    print('Divisors found:', file = out_f)
    if fact_p['knowndiv']:
      print(' knowndiv: {0:d}'.format(fact_p['knowndiv']), file = out_f)

    r = 1
    for dd in sorted(set(fact_p['divisors'])):
      print('r{0:d}={1:d} (pp{2:d})'.format(r, dd, len(str(dd))), file = out_f)
      r += 1

    print('Version: {0:s}'.format(version), file = out_f)
    print('Total time: {0:1.2f} hours.'.format(total_time), file = out_f)
    print('Scaled time: {0:1.2f} units (timescale= {1:1.3f}).'
            .format(total_time * timescale, timescale))

    print('Factorization parameters were as follows:', file = out_f)
    with open(NAME + '.poly', 'r') as in_f:
      for l in in_f:
        l  = chomp(l)
        print(l, file = out_f)

    siever_side = 'rational' if lats_p['lss'] else 'algebraic'
    print('Factor base limits: {0:d}/{1:d}'.format(lats_p['rlim'], lats_p['alim']), file = out_f)
    print('Large primes per side: {0:d}'.format(LARGEP), file = out_f)
    print('Large prime bits: {0:d}/{1:d}'.format(lats_p['lpbr'], lats_p['lpba']), file = out_f)
    print('Sieved {0:s} special-q in [{1:d}, {2:d})'.format(siever_side, min_q, max_q), file = out_f)
    print('Total raw relations: {0:d}'.format(lats_p['currels']), file = out_f)
    print('Relations: {0:s}'.format(rels), file = out_f)
    print('Pruned matrix : {0:s}'.format(prunedmat), file = out_f)
    print('Polynomial selection time: {0:1.2f} hours.'.format(psTime), file = out_f)
    print('Total sieving time: {0:1.2f} hours.'.format(sieve_time), file = out_f)
    print('Total relation processing time: {0:1.2f} hours.'.format(relproc_time), file = out_f)
    print('Matrix solve time: {0:1.2f} hours.'.format(matrix_time), file = out_f)
    print('time per square root: {0:1.2f} hours.'.format(sqrt_time), file = out_f)

    if fact_p['type'] == 'snfs':

      fact_p['digs'] = fact_p['snfs_difficulty']
      DFL = ('{0[type]:s},{0[digs]:d},{1[degree]:d},{3:d},{4:d},{5:g},{6:g},{7:d},'
             '{8:d},{9:d},{10:d},{2[rlim]:d},{2[alim]:d},{2[lpbr]:d},{2[lpba]:d},'
             '{2[mfbr]:d},{2[mfba]:d},{2[rlambda]:g},{2[alambda]:g},{2[qintsize]:d}'
             .format(fact_p, poly_p, lats_p, 0,0,0,0,0,0,0,0))
    else:

      fact_p['digs'] = fact_p['dec_digits'] - 1
      DFL = ('{0[type]:s},{0[digs]:d},{1[degree]:d},{2[maxs1]:d},{2[maxskew]:d},'
             '{2[goodscore]:g},{2[examinefrac]:g},{2[j0]:d},{2[j1]:d},{2[estepsize]:d},'
             '{2[maxtime]:d},{3[rlim]:d},{3[alim]:d},{3[lpbr]:d},{3[lpba]:d},'
             '{3[mfbr]:d},{3[mfba]:d},{3[rlambda]:g},{3[alambda]:g},{3[qintsize]:d}'
             .format(fact_p, poly_p, pols_p, lats_p))

    print('Prototype def-par.txt line would be: {0:s}'.format(DFL), file = out_f)
    print('total time: {0:1.2f} hours.'.format(total_time), file = out_f)

    print(platform.processor(), file = out_f)
    t = platform.platform()
    if len(t):
      print(platform.platform(), file = out_f)
    print('processors: {0:d}, speed: {1:.2f}GHz'
          .format(multiprocessing.cpu_count(), proc_speed()), file = out_f)
  output('-> Factorization summary written to {0:s}'.format(sum_name))
  
def exit_handler():
  terminate_siever(0, 0)

  
def runthatshit():
	# ###########################################
	# ########## Begin execution here ###########
	# ###########################################

	print('-> ________________________________________________________________')
	print('-> | Running factmsieve.py, a Python driver for MSIEVE with GGNFS |')
	print('-> | sieving support. It is Copyright, 2010, Brian Gladman and is |')
	print('-> | a conversion of factmsieve.pl that is Copyright, 2004, Chris |')
	print('-> | Monico.   Version 0.74 (Python 2.6 or later) 19th July 2010. |')
	print('-> |______________________________________________________________|')

	if len(sys.argv) != 2 and len(sys.argv) != 4:
	  print('USAGE: {0:s} <number file | poly file| msieve poly file> [ id  num]'
						  .format(sys.argv[0]))
	  print('  where <polynomial file> is a file with the poly info to use')
	  print('  or <number file> is a file containing the number to factor.')
	  print('  Optional: id/num specifies that this is client <id> of <num>')
	  print('            clients total (clients are numbered 1,2,3,...).')
	  print(' (Multi-client mode is still very experimental - it should only')
	  print('  be used for testing, and is only intended as a hack for running')
	  print('  conveniently on a very small number of machines - perhaps 5 - 10).')
	  sys.exit(-1)

	NAME = sys.argv[1]
	NAME = re.sub('\.(poly|fb|n)', '', NAME)

	# NOTE: These names are global

	LOGNAME  = NAME + '.log'
	JOBNAME  = NAME + '.job'
	ININAME  = NAME + '.ini'
	DATNAME  = NAME + '.dat'
	FBNAME   = NAME + '.fb'
	DEPFNAME = DATNAME + '.dep'
	COLSNAME = DATNAME + '.cyc'
	SIEVER_OUTPUTNAME = 'spairs.out'
	SIEVER_ADDNAME    = 'spairs.add'

	signal.signal(signal.SIGINT, sig_exit)

	if len(sys.argv) == 4:
		client_id = int(sys.argv[2])
		num_clients = int(sys.argv[3])
		if client_id < 1 or client_id > num_clients:
		  die('-> Error: client id should be between 1 and the number of clients {0:d}'
							.format(num_clients))
		PNUM += client_id
	else:
		num_clients = 1
		client_id = 1

	output('-> factmsieve.py (v0.74)', console=False)
	output('-> This is client {0:d} of {1:d}'.format(client_id, num_clients))
	output('-> Running on {0:d} Core{1:s} with {2:d} hyper-thread{3:s} per Core'
			.format(NUM_CORES, ('' if NUM_CORES == 1 else 's'), 
					THREADS_PER_CORE, ('' if THREADS_PER_CORE == 1 else 's')))
	output('-> Working with NAME = {0:s}'.format(NAME))

	if client_id > 1:
	  JOBNAME += '.' + str(client_id)
	  SIEVER_OUTPUTNAME += '.' + str(client_id)
	  SIEVER_ADDNAME += '.' + str(client_id)

	psTime = 0
	check_binary(MSIEVE)

	# Is there a poly file already, or do we need to create one?
	if not os.path.exists(NAME + '.poly'):
	  if os.path.exists(NAME + '.fb'):
		output('-> Converting msieve polynomial (*.fb) to ggnfs (*.poly) format.')
		fb_to_poly()
	  else:
		print('-> Error: Polynomial file {0:s}.poly does not exist!'.format(NAME))
		if num_clients > 1:
		  die('-> Script does not support polynomial search across multiple clients!')
		delete_file(PARAMFILE)
		if os.path.exists(NAME + '.n'):
		  with open(NAME + '.n', 'r') as in_f:
			numberinf = in_f.readlines()
		  t = grep_l('^n:', numberinf)
		  if len(t):
			m = re.search('n:\s*(\d+)', t[0])
		  if len(t) and m and len(m.group(1)):
			fact_p['n'] = int(m.group(1))
			fact_p['dec_digits'] = len(m.group(1))
			print('-> Found n = {0:d}.'.format(fact_p['n']))
			if probable_prime_p(fact_p['n'], 10):
			  die ('-> Error:  n is probably prime!')
			output('-> Running polynomial selection ...')
			if fact_p['dec_digits'] < 98:
			  USE_KLEINJUNG_FRANKE_PS = 0
			psTime = time.time()
			if USE_KLEINJUNG_FRANKE_PS:
			  run_pol5(fact_p, pol5_p, lats_p, clas_p)
			elif USE_MSIEVE_POLY:
			  if not run_msieve_poly(fact_p):
				output_summary(NAME, fact_p, pols_p, poly_p, lats_p)
				sys.exit(0)
			else:
			  run_poly_select(fact_p, pols_p, lats_p, clas_p)
			psTime = (time.time() - psTime) / 3600.0
			if not os.path.exists(NAME + '.poly'):
			  die('Polynomial selection failed.')
		  else:
			output('-> Could not find a number in the file {0:s}.n'.format(NAME))
			die('-> Did you forget the \'n:\' tag?')

	# Read and verify parameters for the factorization.
	if not os.path.exists(NAME + '.poly'):
	  die('Cannot find {0:s}.poly'.format(NAME))

	read_parameters(fact_p, poly_p, lats_p)
	check_parameters(fact_p, poly_p, lats_p)
	if not os.path.exists(DEPFNAME):
	  output('-> Running setup ...')
	  setup(fact_p, poly_p, lats_p, client_id, num_clients, SV_THREADS)

	atexit.register(exit_handler)

	# Do some classical sieving, if needed/applicable.
	if client_id > 1:
	  DOCLASSICAL = 0
	if DOCLASSICAL:
	  output('-> Running classical siever ...')
	  run_classical_sieve(clas_p['cl_a'], 1, clas_p['cl_b'])

	# Finally, sieve until we have reached the desired min # of FF's.
	output('-> Running lattice siever ...')
	run_siever(client_id, num_clients, SV_THREADS, fact_p, lats_p)

	if client_id > 1:
	  print('Client {0:d} terminating...'.format(client_id))
	  sys.exit(0)

	# Obviously, the matrix solving step.
	if not os.path.exists(DEPFNAME):
	  output('-> Running matrix solving step ...')
	  ret = run_msieve('-t {0:d} -nc2'.format(LA_THREADS))
	  if ret:
		die('Return value {0:d}. Terminating...'.format(ret))
	  if not os.path.exists(DEPFNAME):
		die('Some error occurred and matsolve did not record dependencies.')
	else:
	  print('-> File \'deps\' already exists. Proceeding to sqrt step.')

	# summary file name
	if fact_p['type'] == 'gnfs':
	  tmp = 'g' + str(fact_p['dec_digits'])
	else :
	  tmp = 's' + str(fact_p['snfs_difficulty'])

	if not os.path.exists(summary_name(NAME, fact_p)):
	  output('-> Running square root step ...')

	# Do as many square root jobs as needed to get the final factorization
	  ret = run_msieve('-t {0:d} -nc3'.format(LA_THREADS))

	if CLEANUP:
	  for f in glob.iglob('cols*'):
		delete_file(f)
	  for f in glob.iglob('deps*'):
		delete_file(f)
	  delete_file('factor.easy')
	  for f in glob.iglob('rels*'):
		delete_file(f)
	  delete_file('spairs.out')
	  delete_file('spairs.out.gz')
	  delete_file(NAME + '.fb')
	  for f in glob.iglob('*.afb.0'):
		delete_file(f)
	  delete_file('tmpdata.000')
	  delete_file(PARAMFILE)

	output_summary(NAME, fact_p, pols_p, poly_p, lats_p)
	for i in range(5):
	  sys.stdout.write('\a')
	  sys.stdout.flush()
	  time.sleep(0.5)
