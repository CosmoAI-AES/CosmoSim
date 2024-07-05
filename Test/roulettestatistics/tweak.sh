#! /bin/sh

./tweak.py

pyd=../../CosmoSimPy

for i in roulette-*.csv
do
   f=`basename $i .csv`
   mkdir $f
   echo Generating images for $f
   python3 $pyd/roulettegen.py -Z 600 --csvfile $i --xireference -D $f -R --nterms 5
done
