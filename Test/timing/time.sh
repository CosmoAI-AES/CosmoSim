#! /bin/bash

( cd ../.. && cmake --build build ) || exit 1

opt=$*

pdir=../../CosmoSimPy
dir1=/tmp/SampledSIS
dir2=/tmp/RouletteSIS
diffdir=/tmp/diff

mkdir -p $dir1 $dir2 $diffdir

fn=time.csv

echo Sampled Model
/usr/bin/time  python3 $pdir/datagen.py $opt --config ss --directory="$dir1" --csvfile $fn $* >/dev/null
echo Regular Roulette Model
/usr/bin/time python3 $pdir/datagen.py $opt --config fs --directory="$dir2" --csvfile $fn $* >/dev/null

