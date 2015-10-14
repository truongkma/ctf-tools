#!/bin/sh

# Call pkcrack and evaluate its output. It should look like this:
# ...
# Stage 1 completed. Starting stage 2 on Mon Dec 30 13:56:12 2002
# Ta-daaaaa! key0=64799c96, key1=b303049c, key2=a253270a
# Probabilistic test succeeded for 6508 bytes.
# Strange... had a false hit.
# Stage 2 completed. Starting password search on Mon Dec 30 13:56:34 2002
# Key: 61
# Or as a string: 'a' (without the enclosing single quotes)
# Finished on Mon Dec 30 13:56:34 2002
#
# Of interest are the lines starting with "Ta-daaa" and "Or as a string".
# The values contained there are compared to the values given on the
# command line.

if [ $# != 5 ]; then
    echo Usage: $0 crypt.zip plain.zip crypted.file plaintext.file password
    exit 1
fi

output=`mktemp test.sh.out.XXXXXX`

../src/pkcrack -C $1 -P $2 -c $3 -p $4 -d /dev/null >$output 2>&1

if [ `grep -c 'Ta-daaa' $output` -lt 1 ]; then
    echo Keys not found\!
    exit 1
fi

#if [ `grep -c '^Or as a string' $output` -lt 1 ]; then
#    echo Password not found\!
#    exit 1
#fi

set `../src/makekey "$5"` "$5"

if [ `grep Ta-daaa $output | sed 's/\(key.=\) /\10/g' | grep -c "Ta-daaa.* key0=$1, key1=$2, key2=$3"` -lt 1 ]; then
    echo Wrong keys found\!
    exit 1
fi

#if [ `grep -c "^Or as a string: '$4'" $output` -lt 1 ]; then
#    echo Wrong password found\!
#    exit 1
#fi

rm -f $output

exit 0

