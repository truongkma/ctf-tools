#!/bin/bash
# change IFS (Internal Field Separator) variable
# to properly loop over filenames with spaces
export SAVEIFS=$IFS
export IFS=$(echo -en "\n\b")
found=0
n=1
while :
#while [ $n -le 10000 ]  ---- chay n den 10000
#while (( $n <= 9207 ))
do
for z in *.zip;
do
d=`basename $z`
unzip $z
rm -rf $z
done
done
export IFS=$SAVEIFS
