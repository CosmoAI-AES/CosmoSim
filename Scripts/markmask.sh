#!/bin/sh

# This script reads a CSV file with source and lens parameters and 
# generate corresponding images.
# This is similar to polargen and olddatagen, except that it uses
# the testmask program which adds masking.
#
# Useful options:
# -R    to draw axes and box the plot
# -Z n  to change the image size

pwd
echo $0 $1
which testmask

IFS=,
read -r header
echo $header
while read -r idx fn srcmode lensmode chi x y einsteinr sigma sigma2 theta nterms
do
  idx=`echo $idx | tr -d '"'`
  testmask $* -X $chi -x $x -y $y -E $einsteinr \
	        -s $sigma -2 $sigma2 -t $theta -n $nterms \
                -S $srcmode -L $lensmode -N $idx 
done
