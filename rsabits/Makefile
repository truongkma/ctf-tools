#
# Implementation for "Reconstructing RSA Private Keys from Random Key
# Bits," in proc. Crypto 2009, vol. 5677 of LNCS, pp. 1--17.
# Springer-Verlag, Aug. 2009.
#
# Written by Nadia Heninger and Hovav Shacham.
#
# Copyright (c) 2009, The Regents of the University of California.
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# 3. Neither the name of the University nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

# these (uppercase) variables apply to gmake-builtin rules
CPPFLAGS := -I/usr/local/include
warnflags := -Wall #-W
CXXFLAGS := -O2 -m64 -g $(warnflags) #-pipe -ffast-math -fomit-frame-pointer
LDFLAGS := -L/usr/local/lib
LDLIBS := -lntl -lgmp -lm

srcs := rsa.C keygen.C
objs := $(srcs:.C=.o)

binaries := $(srcs:.C=)

.PHONY: target dist clean spotless depend

target: $(binaries)

clean:
	-rm -f $(binaries) $(objs)

spotless: clean
	-rm -f Makefile.bak *~ core

# we do not give any -I info because we want to depend only
# on stuff in the current directory
depend:
	makedepend -Y -- $(CFLAGS) -- $(srcs) 2> /dev/null

# DO NOT DELETE
