#!/bin/sh

pyd=../../CosmoSimPy/

mkdir -p Original Roulette diff montage

python3 $pyd/datagen.py -Z 600 --csvfile debug.csv --outfile roulette.csv \
   --model Roulette --centred -D Original --actual  -R
   # | tee datagen.log || exit 1
python3 $pyd/roulettegen.py -n 10 -Z 600 --csvfile roulette.csv --centred -D Roulette -R
   # tee roulettegen.log || exit 2
mkdir -p Actual
mv Original/actual-* Actual
python3 $pyd/compare.py --diff diff/ --masked Original Roulette 

for i in diff/*
do
   f=`basename $i`
   convert \( Actual/actual-$f Original/$f +append \) \( diff/$f Roulette/$f +append \) -append montage/$f
done

