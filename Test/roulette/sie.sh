#! /bin/sh

CONVERT=convert

opt=$*

pdir=../../CosmoSimPy/
fn=sie.csv

mkdir -p Raytrace actual montage
python3 $pdir/datagen.py $opt --model "Raytrace" --directory="Raytrace" --csvfile $fn  --actual -R
mv Raytrace/actual*png actual

for m in 3 5 15
do
   mkdir -p Roulette$m  diff$m
   python3 $pdir/datagen.py $opt --model "Roulette" --directory="Roulette$m" --csvfile $fn  --nterms $m -R
   python3 $pdir/compare.py --diff diff$m Raytrace Roulette$m
done


for f in Raytrace/*
do
  ff=`basename $f`
  $CONVERT \( actual/actual-$ff Raytrace/$ff +append \) \
     \( Roulette3/$ff diff3/$ff +append \) \
     \( Roulette5/$ff diff5/$ff +append \) \
     \( Roulette15/$ff diff15/$ff +append \) \
     -append montage/$ff
done
