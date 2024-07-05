#! /bin/sh

./tweak.py
./txt.py

pyd=../../CosmoSimPy

for i in roulette-*.csv
do
   f=`basename $i .csv`
   mkdir $f
   echo Generating images for $f
   python3 $pyd/roulettegen.py -Z 600 --csvfile $i --xireference -D $f -R --nterms 5
done

mkdir Raytrace
python3 $pyd/datagen.py -Z 600 --csvfile dataset.csv \
   --model Raytrace --lens SIS --xireference -D Raytrace  -R 
